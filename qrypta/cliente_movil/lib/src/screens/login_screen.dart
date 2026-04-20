import 'package:flutter/material.dart';
import 'package:flutter_form_builder/flutter_form_builder.dart';
import 'package:form_builder_validators/form_builder_validators.dart';
import 'package:qrypta_cliente_flutter/src/services/identity_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key, required this.identityService});

  final IdentityService identityService;

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final GlobalKey<FormBuilderState> _formKey = GlobalKey<FormBuilderState>();
  bool _busy = false;
  String? _status;

  Future<void> _login() async {
    final form = _formKey.currentState;
    if (form == null || !form.saveAndValidate()) {
      setState(() => _status = 'Revisa los datos del formulario');
      return;
    }

    final mnemonic = (form.value['mnemonic'] as String? ?? '').trim();

    setState(() {
      _busy = true;
      _status = null;
    });

    try {
      await widget.identityService.importFromMnemonic(mnemonic);
      if (!mounted) {
        return;
      }
      setState(() => _status = 'Sesión restaurada correctamente');
      Navigator.of(context).pop(true);
    } catch (e) {
      setState(() => _status = 'Error de login: $e');
    } finally {
      setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    final horizontalPadding = width >= 900 ? (width - 760) / 2 : 16.0;

    return Scaffold(
      appBar: AppBar(title: const Text('Login local')),
      body: Padding(
        padding: EdgeInsets.fromLTRB(horizontalPadding, 16, horizontalPadding, 16),
        child: FormBuilder(
          key: _formKey,
          child: ListView(
            shrinkWrap: true,
            children: [
              FormBuilderTextField(
                name: 'mnemonic',
                minLines: 2,
                maxLines: 4,
                textInputAction: TextInputAction.done,
                validator: FormBuilderValidators.compose([
                  FormBuilderValidators.required(errorText: 'La mnemonic es obligatoria'),
                  (valueCandidate) {
                    final value = (valueCandidate ?? '').trim();
                    if (value.isEmpty) {
                      return null;
                    }
                    final wordCount = value.split(RegExp(r'\s+')).where((word) => word.isNotEmpty).length;
                    if (wordCount != 12 && wordCount != 24) {
                      return 'La mnemonic debe tener 12 o 24 palabras';
                    }
                    return null;
                  },
                ]),
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  labelText: 'Mnemonic BIP-39',
                ),
              ),
              const SizedBox(height: 10),
              ElevatedButton(
                onPressed: _busy ? null : _login,
                child: const Text('Iniciar sesión'),
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
