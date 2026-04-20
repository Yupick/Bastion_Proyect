import 'package:flutter/material.dart';
import 'package:qrypta_cliente_flutter/shared/app_theme_controller.dart';
import 'package:qrypta_cliente_flutter/src/screens/bootstrap_screen.dart';
import 'package:qrypta_cliente_flutter/src/services/app_di_container.dart';
import 'package:qrypta_cliente_flutter/src/services/model_hive_adapters.dart';

class QryptaApp extends StatefulWidget {
  const QryptaApp({super.key});

  @override
  State<QryptaApp> createState() => _QryptaAppState();
}

class _QryptaAppState extends State<QryptaApp> {
  late final Future<void> _setupFuture;

  @override
  void initState() {
    super.initState();
    _setupFuture = _setup();
  }

  Future<void> _setup() async {
    final di = AppDiContainer.instance;
    registerHiveAdapters();
    await di.localStorage.init();
    await di.messageCache.init();
    await di.pushNotifications.initialize();
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<void>(
      future: _setupFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const MaterialApp(
            home: Scaffold(body: Center(child: CircularProgressIndicator())),
          );
        }

        return ValueListenableBuilder<ThemeMode>(
          valueListenable: AppThemeController.mode,
          builder: (context, mode, _) {
            return MaterialApp(
              title: 'Qrypta Mobile',
              debugShowCheckedModeBanner: false,
              themeMode: mode,
              theme: ThemeData(
                colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF007A5A)),
                useMaterial3: true,
              ),
              darkTheme: ThemeData(
                colorScheme: ColorScheme.fromSeed(
                  seedColor: const Color(0xFF007A5A),
                  brightness: Brightness.dark,
                ),
                useMaterial3: true,
              ),
              home: const BootstrapScreen(),
            );
          },
        );
      },
    );
  }
}
