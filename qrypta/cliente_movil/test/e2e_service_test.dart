import 'package:flutter_test/flutter_test.dart';
import 'package:qrypta_cliente_flutter/src/models/identity.dart';
import 'package:qrypta_cliente_flutter/src/services/e2e_service.dart';

void main() {
  group('E2eService', () {
    final service = E2eService();

    test('genera firma de handshake y la valida', () async {
      final peerId = List<String>.filled(64, 'a').join();
      final identity = LocalIdentity(
        peerId: peerId,
        publicKeyB64: 'cHVibGlj',
        privateKeyB64: 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',
        mnemonic: 'test test test test test test test test test test test junk',
      );

      final signature = await service.createHandshakeSignature(
        local: identity,
        challenge: 'hello',
      );

      expect(signature.isNotEmpty, true);
    });

    test('encapsulación placeholder retorna base64', () async {
      final key = await service.encapsulateSessionKeyPlaceholder(
        peerA: 'peer-a',
        peerB: 'peer-b',
      );

      expect(key.isNotEmpty, true);
    });

    test('firma PQC de handshake (ML-DSA) valida correctamente', () async {
      final kp = await service.generateDilithiumKeyPair();
      final sigEnvelope = await service.createHandshakeSignaturePqc(
        challenge: 'pqc-hello',
        peerId: 'peer-pqc-1',
        privateKeyB64: kp.$2,
      );

      final valid = await service.verifyHandshakeSignaturePqc(
        challenge: 'pqc-hello',
        peerId: 'peer-pqc-1',
        publicKeyB64: kp.$1,
        signatureEnvelopeB64: sigEnvelope,
      );

      expect(valid, isTrue);
    });

    test('encapsulación/decapsulación Kyber (ML-KEM) coincide', () async {
      final kp = await service.generateKyberKeyPair();

      final encapsulated = await service.encapsulateSessionKeyKyber(
        recipientPublicKeyB64: kp.$1,
      );

      final decapsulated = await service.decapsulateSessionKeyKyber(
        ciphertextB64: encapsulated.$1,
        recipientPrivateKeyB64: kp.$2,
      );

      expect(decapsulated, equals(encapsulated.$2));
    });

    test('ratchet avanza claves y mantiene sincronía entre pares', () async {
      final sender = await service.initializeRatchet(
        sharedSecretB64: 'c2hhcmVkLXNlY3JldA==',
        localPeerId: 'peer-a',
        remotePeerId: 'peer-b',
      );

      final receiver = await service.initializeRatchet(
        sharedSecretB64: 'c2hhcmVkLXNlY3JldA==',
        localPeerId: 'peer-b',
        remotePeerId: 'peer-a',
      );

      final senderStep1 = await service.nextMessageKey(state: sender);
      final receiverStep1 = await service.nextMessageKey(state: receiver);
      final senderStep2 = await service.nextMessageKey(state: senderStep1.$1);

      expect(senderStep1.$2, equals(receiverStep1.$2));
      expect(senderStep2.$2, isNot(equals(senderStep1.$2)));
      expect(senderStep2.$1.step, equals(2));
    });
  });
}
