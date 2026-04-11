class LocalIdentity {
  const LocalIdentity({
    required this.peerId,
    required this.publicKeyB64,
    required this.privateKeyB64,
    required this.mnemonic,
  });

  final String peerId;
  final String publicKeyB64;
  final String privateKeyB64;
  final String mnemonic;
}
