import 'package:flutter/material.dart';
import 'package:qrypta_cliente_flutter/src/models/identity.dart';
import 'package:qrypta_cliente_flutter/src/screens/chat_screen.dart';
import 'package:qrypta_cliente_flutter/src/screens/onboarding_screen.dart';
import 'package:qrypta_cliente_flutter/src/services/identity_service.dart';

class BootstrapScreen extends StatefulWidget {
  const BootstrapScreen({super.key});

  @override
  State<BootstrapScreen> createState() => _BootstrapScreenState();
}

class _BootstrapScreenState extends State<BootstrapScreen> {
  final IdentityService _identityService = IdentityService();
  Future<LocalIdentity?>? _identityFuture;

  @override
  void initState() {
    super.initState();
    _identityFuture = _identityService.loadIdentity();
  }

  void _refresh() {
    setState(() {
      _identityFuture = _identityService.loadIdentity();
    });
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<LocalIdentity?>(
      future: _identityFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Scaffold(body: Center(child: CircularProgressIndicator()));
        }

        final identity = snapshot.data;
        if (identity == null) {
          return OnboardingScreen(
            identityService: _identityService,
            onDone: _refresh,
          );
        }

        return ChatScreen(identity: identity, onReset: _refresh);
      },
    );
  }
}
