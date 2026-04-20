import 'dart:convert';
import 'dart:typed_data';

import 'package:cryptography/cryptography.dart';
import 'package:liboqs/liboqs.dart' as oqs;
import 'package:qrypta_cliente_flutter/src/models/identity.dart';

class DecryptedPayload {
  const DecryptedPayload({required this.senderPeerId, required this.message});

  final String senderPeerId;
  final String message;
}

class RatchetState {
  const RatchetState({
    required this.chainKeyB64,
    required this.step,
  });

  final String chainKeyB64;
  final int step;
}

class E2eService {
  E2eService() {
    if (!_libOqsInitialized) {
      oqs.LibOQS.init();
      _libOqsInitialized = true;
    }
  }

  static bool _libOqsInitialized = false;

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

  Future<String> createHandshakeSignature({
    required LocalIdentity local,
    required String challenge,
  }) async {
    final keyPair = await _ed25519.newKeyPairFromSeed(base64Decode(local.privateKeyB64));
    final signature = await _ed25519.sign(
      utf8.encode('handshake:$challenge:${local.peerId}'),
      keyPair: keyPair,
    );
    return base64Encode(signature.bytes);
  }

  Future<bool> verifyHandshakeSignature({
    required String challenge,
    required String peerId,
    required String publicKeyB64,
    required String signatureB64,
  }) async {
    final pubBytes = base64Decode(publicKeyB64);
    final computedPeerId = _toHex(await Sha256().hash(pubBytes).then((v) => v.bytes));
    if (computedPeerId != peerId) {
      return false;
    }

    return _ed25519.verify(
      utf8.encode('handshake:$challenge:$peerId'),
      signature: Signature(
        base64Decode(signatureB64),
        publicKey: SimplePublicKey(pubBytes, type: KeyPairType.ed25519),
      ),
    );
  }

  Future<String> encapsulateSessionKeyPlaceholder({
    required String peerA,
    required String peerB,
  }) async {
    final pair = [peerA, peerB]..sort();
    final material = utf8.encode('kyber-placeholder:${pair[0]}:${pair[1]}');
    final digest = await Sha256().hash(material);
    return base64Encode(digest.bytes);
  }

  Future<(String publicKeyB64, String privateKeyB64)> generateDilithiumKeyPair({
    String algorithm = 'ML-DSA-65',
  }) async {
    final signature = oqs.Signature.create(algorithm);
    try {
      final kp = signature.generateKeyPair();
      return (base64Encode(kp.publicKey), base64Encode(kp.secretKey));
    } finally {
      signature.dispose();
    }
  }

  Future<(String publicKeyB64, String privateKeyB64)> generateKyberKeyPair({
    String algorithm = 'ML-KEM-768',
  }) async {
    final kem = oqs.KEM.create(algorithm);
    try {
      final kp = kem.generateKeyPair();
      return (base64Encode(kp.publicKey), base64Encode(kp.secretKey));
    } finally {
      kem.dispose();
    }
  }

  Future<String> createHandshakeSignaturePqc({
    required String challenge,
    required String peerId,
    required String privateKeyB64,
    String algorithm = 'ML-DSA-65',
  }) async {
    final signature = oqs.Signature.create(algorithm);
    try {
      final message = utf8.encode('handshake:$challenge:$peerId');
      final sigBytes = signature.sign(
        Uint8List.fromList(message),
        base64Decode(privateKeyB64),
      );

      return base64Encode(
        utf8.encode(
          jsonEncode(<String, String>{
            'alg': algorithm,
            'sig': base64Encode(sigBytes),
          }),
        ),
      );
    } finally {
      signature.dispose();
    }
  }

  Future<bool> verifyHandshakeSignaturePqc({
    required String challenge,
    required String peerId,
    required String publicKeyB64,
    required String signatureEnvelopeB64,
  }) async {
    final envelope = jsonDecode(
      utf8.decode(base64Decode(signatureEnvelopeB64)),
    ) as Map<String, dynamic>;

    final algorithm = envelope['alg'] as String? ?? 'ML-DSA-65';
    final sigB64 = envelope['sig'] as String?;
    if (sigB64 == null || sigB64.isEmpty) {
      return false;
    }

    final signature = oqs.Signature.create(algorithm);
    try {
      final message = utf8.encode('handshake:$challenge:$peerId');
      return signature.verify(
        Uint8List.fromList(message),
        base64Decode(sigB64),
        base64Decode(publicKeyB64),
      );
    } finally {
      signature.dispose();
    }
  }

  Future<(String ciphertextB64, String sharedSecretB64)> encapsulateSessionKeyKyber({
    required String recipientPublicKeyB64,
    String algorithm = 'ML-KEM-768',
  }) async {
    final kem = oqs.KEM.create(algorithm);
    try {
      final result = kem.encapsulate(base64Decode(recipientPublicKeyB64));
      return (base64Encode(result.ciphertext), base64Encode(result.sharedSecret));
    } finally {
      kem.dispose();
    }
  }

  Future<String> decapsulateSessionKeyKyber({
    required String ciphertextB64,
    required String recipientPrivateKeyB64,
    String algorithm = 'ML-KEM-768',
  }) async {
    final kem = oqs.KEM.create(algorithm);
    try {
      final secret = kem.decapsulate(
        base64Decode(ciphertextB64),
        base64Decode(recipientPrivateKeyB64),
      );
      return base64Encode(secret);
    } finally {
      kem.dispose();
    }
  }

  Future<RatchetState> initializeRatchet({
    required String sharedSecretB64,
    required String localPeerId,
    required String remotePeerId,
  }) async {
    final pair = [localPeerId, remotePeerId]..sort();
    final digest = await Sha256().hash(
      Uint8List.fromList(
        utf8.encode('ratchet:init:${pair[0]}:${pair[1]}:$sharedSecretB64'),
      ),
    );

    return RatchetState(chainKeyB64: base64Encode(digest.bytes), step: 0);
  }

  Future<(RatchetState state, String messageKeyB64)> nextMessageKey({
    required RatchetState state,
  }) async {
    final chainKey = base64Decode(state.chainKeyB64);
    final messageDigest = await Sha256().hash(
      Uint8List.fromList(
        <int>[
          ...chainKey,
          ...utf8.encode(':msg:${state.step}'),
        ],
      ),
    );

    final nextChainDigest = await Sha256().hash(
      Uint8List.fromList(
        <int>[
          ...chainKey,
          ...utf8.encode(':chain:${state.step}'),
        ],
      ),
    );

    final nextState = RatchetState(
      chainKeyB64: base64Encode(nextChainDigest.bytes),
      step: state.step + 1,
    );

    return (nextState, base64Encode(messageDigest.bytes));
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
