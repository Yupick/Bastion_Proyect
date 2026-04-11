import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:qrypta_cliente_flutter/src/models/identity.dart';

class LocalIdentityStore {
  static const _kPeerId = 'peer_id';
  static const _kPublicKey = 'public_key_b64';
  static const _kPrivateKey = 'private_key_b64';
  static const _kMnemonic = 'mnemonic';

  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  Future<LocalIdentity?> read() async {
    final peerId = await _storage.read(key: _kPeerId);
    final publicKey = await _storage.read(key: _kPublicKey);
    final privateKey = await _storage.read(key: _kPrivateKey);
    final mnemonic = await _storage.read(key: _kMnemonic);

    if (peerId == null || publicKey == null || privateKey == null || mnemonic == null) {
      return null;
    }

    return LocalIdentity(
      peerId: peerId,
      publicKeyB64: publicKey,
      privateKeyB64: privateKey,
      mnemonic: mnemonic,
    );
  }

  Future<void> save(LocalIdentity identity) async {
    await _storage.write(key: _kPeerId, value: identity.peerId);
    await _storage.write(key: _kPublicKey, value: identity.publicKeyB64);
    await _storage.write(key: _kPrivateKey, value: identity.privateKeyB64);
    await _storage.write(key: _kMnemonic, value: identity.mnemonic);
  }

  Future<void> clear() async {
    await _storage.deleteAll();
  }

  String encodeBase64(List<int> bytes) => base64Encode(bytes);
}
