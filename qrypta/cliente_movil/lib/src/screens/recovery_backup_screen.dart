import 'package:flutter/material.dart';
import 'package:flutter_form_builder/flutter_form_builder.dart';
import 'package:form_builder_validators/form_builder_validators.dart';
import 'package:qrypta_cliente_flutter/src/services/backup_service.dart';
import 'package:qrypta_cliente_flutter/src/services/local_identity_store.dart';

class RecoveryBackupScreen extends StatefulWidget {
  const RecoveryBackupScreen({
    super.key,
    required this.backupService,
    required this.identityStore,
  });

  final BackupService backupService;
  final LocalIdentityStore identityStore;

  @override
  State<RecoveryBackupScreen> createState() => _RecoveryBackupScreenState();
}

class _RecoveryBackupScreenState extends State<RecoveryBackupScreen> {
  final GlobalKey<FormBuilderState> _formKey = GlobalKey<FormBuilderState>();
  bool _busy = false;
  String? _status;

  Future<void> _restore() async {
    final form = _formKey.currentState;
    if (form == null || !form.saveAndValidate()) {
      setState(() => _status = 'Revisa los datos del formulario');
      return;
    }

    final blob = (form.value['blob'] as String? ?? '').trim();
    final pass = (form.value['passphrase'] as String? ?? '').trim();

    setState(() {
      _busy = true;
      _status = null;
    });

    try {
      final identity = await widget.backupService.importEncrypted(
        encryptedBlob: blob,
        passphrase: pass,
      );
      await widget.identityStore.save(identity);
      if (!mounted) {
        return;
      }
      setState(() => _status = 'Backup restaurado correctamente');
      Navigator.of(context).pop(true);
    } catch (e) {
      setState(() => _status = 'Error restaurando backup: $e');
    } finally {
      setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    final horizontalPadding = width >= 900 ? (width - 760) / 2 : 16.0;

    return Scaffold(
      appBar: AppBar(title: const Text('Recuperar backup')),
      body: Padding(
        padding: EdgeInsets.fromLTRB(horizontalPadding, 16, horizontalPadding, 16),
        child: FormBuilder(
          key: _formKey,
          child: ListView(
            children: [
            FormBuilderTextField(
              name: 'passphrase',
              obscureText: true,
              validator: FormBuilderValidators.compose([
                FormBuilderValidators.required(errorText: 'La passphrase es obligatoria'),
                FormBuilderValidators.minLength(8, errorText: 'Mínimo 8 caracteres'),
              ]),
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                labelText: 'Passphrase',
              ),
            ),
            const SizedBox(height: 10),
            FormBuilderTextField(
              name: 'blob',
              minLines: 4,
              maxLines: 8,
              validator: FormBuilderValidators.compose([
                FormBuilderValidators.required(errorText: 'El blob cifrado es obligatorio'),
                FormBuilderValidators.minLength(32, errorText: 'Blob cifrado inválido'),
              ]),
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                labelText: 'Blob cifrado',
              ),
            ),
            const SizedBox(height: 10),
            ElevatedButton(
              onPressed: _busy ? null : _restore,
              child: const Text('Restaurar backup'),
            ),
            if (_status != null) ...[
              const SizedBox(height: 10),
              Text(_status!),
            ],
            ],
          ),
        ),
      ),
    );
  }
}
