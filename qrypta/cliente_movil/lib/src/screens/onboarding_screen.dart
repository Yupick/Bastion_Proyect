import 'package:flutter/material.dart';
import 'package:qrypta_cliente_flutter/src/services/identity_service.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({
    super.key,
    required this.identityService,
    required this.onDone,
  });

  final IdentityService identityService;
  final VoidCallback onDone;

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final TextEditingController _mnemonicCtrl = TextEditingController();
  bool _loading = false;
  String? _error;

  Future<void> _create() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      await widget.identityService.createIdentity();
      widget.onDone();
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _import() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      await widget.identityService.importFromMnemonic(_mnemonicCtrl.text);
      widget.onDone();
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Qrypta - Registro local')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Crea o recupera tu identidad local (BIP-39).'),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: _loading ? null : _create,
              child: const Text('Crear identidad nueva'),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _mnemonicCtrl,
              minLines: 2,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: 'Mnemonic de 24 palabras',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 8),
            OutlinedButton(
              onPressed: _loading ? null : _import,
              child: const Text('Importar identidad'),
            ),
            if (_loading) ...[
              const SizedBox(height: 16),
              const LinearProgressIndicator(),
            ],
            if (_error != null) ...[
              const SizedBox(height: 12),
              Text(_error!, style: const TextStyle(color: Colors.red)),
            ],
          ],
        ),
      ),
    );
  }
}
