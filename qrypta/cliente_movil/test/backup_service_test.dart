import 'package:flutter_test/flutter_test.dart';
import 'package:qrypta_cliente_flutter/src/models/identity.dart';
import 'package:qrypta_cliente_flutter/src/services/backup_service.dart';

void main() {
  group('BackupService', () {
    final service = BackupService();

    const identity = LocalIdentity(
      peerId: 'peer-01',
      publicKeyB64: 'PUB',
      privateKeyB64: 'PRIV',
      mnemonic: 'word1 word2 word3',
    );

    test('exporta e importa backup cifrado', () async {
      final blob = await service.exportEncrypted(
        identity: identity,
        passphrase: '12345678',
      );

      final restored = await service.importEncrypted(
        encryptedBlob: blob,
        passphrase: '12345678',
      );

      expect(restored.peerId, identity.peerId);
      expect(restored.privateKeyB64, identity.privateKeyB64);
    });
  });
}
