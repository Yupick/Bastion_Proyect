import 'package:flutter/material.dart';
import 'package:qrypta_cliente_flutter/src/screens/bootstrap_screen.dart';

class QryptaApp extends StatelessWidget {
  const QryptaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Qrypta Mobile',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF007A5A)),
        useMaterial3: true,
      ),
      home: const BootstrapScreen(),
    );
  }
}
