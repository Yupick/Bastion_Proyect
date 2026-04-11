import 'dart:convert';
import 'dart:typed_data';

import 'package:bip39/bip39.dart' as bip39;
import 'package:cryptography/cryptography.dart';
import 'package:qrypta_cliente_flutter/src/models/identity.dart';
import 'package:qrypta_cliente_flutter/src/services/local_identity_store.dart';

class IdentityService {
  IdentityService({LocalIdentityStore? store}) : _store = store ?? LocalIdentityStore();

  final LocalIdentityStore _store;
  final _ed25519 = Ed25519();

  Future<LocalIdentity?> loadIdentity() => _store.read();

  Future<LocalIdentity> createIdentity() async {
    final mnemonic = bip39.generateMnemonic(strength: 256);
    final entropyHex = bip39.mnemonicToEntropy(mnemonic);
    final seed = _hexToBytes(entropyHex);
    final keyPair = await _ed25519.newKeyPairFromSeed(_deriveSeed(seed));
    final privateKeyBytes = await keyPair.extractPrivateKeyBytes();
    final publicKeyBytes = (await keyPair.extractPublicKey()).bytes;
    final peerId = _toHex(await Sha256().hash(publicKeyBytes).then((h) => h.bytes));

    final identity = LocalIdentity(
      peerId: peerId,
      publicKeyB64: base64Encode(publicKeyBytes),
      privateKeyB64: base64Encode(privateKeyBytes),
      mnemonic: mnemonic,
    );
    await _store.save(identity);
    return identity;
  }

  Future<LocalIdentity> importFromMnemonic(String mnemonic) async {
    final normalized = mnemonic.trim().toLowerCase();
    if (!bip39.validateMnemonic(normalized)) {
      throw Exception('Mnemonic invalido');
    }

    final entropyHex = bip39.mnemonicToEntropy(normalized);
    final seed = _hexToBytes(entropyHex);
    final keyPair = await _ed25519.newKeyPairFromSeed(_deriveSeed(seed));
    final privateKeyBytes = await keyPair.extractPrivateKeyBytes();
    final publicKeyBytes = (await keyPair.extractPublicKey()).bytes;
    final peerId = _toHex(await Sha256().hash(publicKeyBytes).then((h) => h.bytes));

    final identity = LocalIdentity(
      peerId: peerId,
      publicKeyB64: base64Encode(publicKeyBytes),
      privateKeyB64: base64Encode(privateKeyBytes),
      mnemonic: normalized,
    );
    await _store.save(identity);
    return identity;
  }

  Uint8List _deriveSeed(Uint8List input) {
    final seed = Uint8List(32);
    for (var i = 0; i < seed.length; i++) {
      seed[i] = input[i % input.length];
    }
    return seed;
  }

  Uint8List _hexToBytes(String hex) {
    final result = Uint8List(hex.length ~/ 2);
    for (var i = 0; i < hex.length; i += 2) {
      result[i ~/ 2] = int.parse(hex.substring(i, i + 2), radix: 16);
    }
    return result;
  }

  String _toHex(List<int> bytes) {
    final out = StringBuffer();
    for (final b in bytes) {
      out.write(b.toRadixString(16).padLeft(2, '0'));
    }
    return out.toString();
  }
}
