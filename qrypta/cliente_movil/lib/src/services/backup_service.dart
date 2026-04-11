import 'dart:convert';

import 'package:cryptography/cryptography.dart';
import 'package:qrypta_cliente_flutter/src/models/identity.dart';

class BackupService {
  Future<String> exportEncrypted({
    required LocalIdentity identity,
    required String passphrase,
  }) async {
    if (passphrase.trim().length < 8) {
      throw Exception('Passphrase demasiado corta');
    }

    final payload = jsonEncode({
      'peerId': identity.peerId,
      'pub': identity.publicKeyB64,
      'priv': identity.privateKeyB64,
      'mnemonic': identity.mnemonic,
      'ts': DateTime.now().toUtc().toIso8601String(),
    });

    final key = await _deriveKey(passphrase);
    final nonce = _nonce();
    final box = await AesGcm.with256bits().encrypt(
      utf8.encode(payload),
      secretKey: key,
      nonce: nonce,
    );

    return base64Encode(
      utf8.encode(
        jsonEncode({
          'alg': 'aes-gcm',
          'nonce': base64Encode(box.nonce),
          'ct': base64Encode(box.cipherText),
          'mac': base64Encode(box.mac.bytes),
        }),
      ),
    );
  }

  Future<LocalIdentity> importEncrypted({
    required String encryptedBlob,
    required String passphrase,
  }) async {
    final map = jsonDecode(utf8.decode(base64Decode(encryptedBlob))) as Map<String, dynamic>;
    final key = await _deriveKey(passphrase);
    final box = SecretBox(
      base64Decode(map['ct'] as String),
      nonce: base64Decode(map['nonce'] as String),
      mac: Mac(base64Decode(map['mac'] as String)),
    );
    final clear = await AesGcm.with256bits().decrypt(box, secretKey: key);
    final identity = jsonDecode(utf8.decode(clear)) as Map<String, dynamic>;

    return LocalIdentity(
      peerId: identity['peerId'] as String,
      publicKeyB64: identity['pub'] as String,
      privateKeyB64: identity['priv'] as String,
      mnemonic: identity['mnemonic'] as String,
    );
  }

  Future<SecretKey> _deriveKey(String passphrase) async {
    final bytes = utf8.encode('qrypta-backup-v1:$passphrase');
    final hash = await Sha256().hash(bytes);
    return SecretKey(hash.bytes);
  }

  List<int> _nonce() {
    final now = DateTime.now().microsecondsSinceEpoch;
    final raw = utf8.encode('$now:${now.hashCode}:qrypta');
    return raw.take(12).toList(growable: false);
  }
}
