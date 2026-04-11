import 'dart:convert';
import 'dart:typed_data';

import 'package:cryptography/cryptography.dart';
import 'package:qrypta_cliente_flutter/src/models/identity.dart';

class DecryptedPayload {
  const DecryptedPayload({required this.senderPeerId, required this.message});

  final String senderPeerId;
  final String message;
}

class E2eService {
  final _ed25519 = Ed25519();

  Future<(String payloadB64, String firmaB64)> encryptAndSign({
    required LocalIdentity local,
    required String destinationPeerId,
    required String clearText,
  }) async {
    final aesKey = await _deriveConversationKey(local.peerId, destinationPeerId);
    final nonce = _nonceFromClock();
    final secretBox = await AesGcm.with256bits().encrypt(
      utf8.encode(clearText),
      secretKey: aesKey,
      nonce: nonce,
    );

    final signingPair = await _ed25519.newKeyPairFromSeed(base64Decode(local.privateKeyB64));
    final signature = await _ed25519.sign(
      secretBox.cipherText,
      keyPair: signingPair,
    );

    final envelope = {
      'alg': 'aes-gcm+ed25519',
      'nonce': base64Encode(secretBox.nonce),
      'ciphertext': base64Encode(secretBox.cipherText),
      'mac': base64Encode(secretBox.mac.bytes),
      'pub': local.publicKeyB64,
      'sig': base64Encode(signature.bytes),
    };

    final payloadB64 = base64Encode(utf8.encode(jsonEncode(envelope)));
    return (payloadB64, base64Encode(signature.bytes));
  }

  Future<DecryptedPayload> decryptIncoming({
    required String myPeerId,
    required String payloadB64,
    required String peerIdOrigen,
  }) async {
    final jsonRaw = utf8.decode(base64Decode(payloadB64));
    final map = jsonDecode(jsonRaw) as Map<String, dynamic>;

    final senderPublicKey = base64Decode(map['pub'] as String);
    final senderPeerId = _toHex(await Sha256().hash(senderPublicKey).then((v) => v.bytes));
    if (senderPeerId != peerIdOrigen) {
      throw Exception('Peer origen no coincide con firma');
    }

    final cipherText = base64Decode(map['ciphertext'] as String);
    final signature = base64Decode(map['sig'] as String);
    final ok = await _ed25519.verify(
      cipherText,
      signature: Signature(signature, publicKey: SimplePublicKey(senderPublicKey, type: KeyPairType.ed25519)),
    );
    if (!ok) {
      throw Exception('Firma invalida');
    }

    final nonce = base64Decode(map['nonce'] as String);
    final mac = Mac(base64Decode(map['mac'] as String));
    final secretBox = SecretBox(cipherText, nonce: nonce, mac: mac);

    final aesKey = await _deriveConversationKey(myPeerId, senderPeerId);
    final clearBytes = await AesGcm.with256bits().decrypt(secretBox, secretKey: aesKey);
    return DecryptedPayload(senderPeerId: senderPeerId, message: utf8.decode(clearBytes));
  }

  Future<SecretKey> _deriveConversationKey(String a, String b) async {
    final pair = [a, b]..sort();
    final material = utf8.encode('${pair[0]}:${pair[1]}:qrypta-mobile-v1');
    final digest = await Sha256().hash(material);
    return SecretKey(Uint8List.fromList(digest.bytes));
  }

  Uint8List _nonceFromClock() {
    final micros = DateTime.now().microsecondsSinceEpoch;
    final bytes = ByteData(12);
    bytes.setInt64(0, micros);
    bytes.setInt32(8, micros.hashCode);
    return bytes.buffer.asUint8List();
  }

  String _toHex(List<int> bytes) {
    final out = StringBuffer();
    for (final b in bytes) {
      out.write(b.toRadixString(16).padLeft(2, '0'));
    }
    return out.toString();
  }
}
