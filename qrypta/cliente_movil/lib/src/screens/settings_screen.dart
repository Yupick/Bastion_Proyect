import 'package:flutter/material.dart';
import 'package:qrypta_cliente_flutter/shared/app_theme_controller.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _darkMode = AppThemeController.isDarkMode;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Ajustes')),
      body: ListView(
        children: [
          SwitchListTile(
            title: const Text('Dark mode'),
            subtitle: const Text('Activar apariencia oscura'),
            value: _darkMode,
            onChanged: (value) {
              setState(() => _darkMode = value);
              AppThemeController.setDarkMode(value);
            },
          ),
          const ListTile(
            leading: Icon(Icons.security),
            title: Text('Privacidad alta'),
            subtitle: Text('Ocultar metadata sensible por defecto'),
          ),
          const ListTile(
            leading: Icon(Icons.notifications_active_outlined),
            title: Text('Notificaciones push'),
            subtitle: Text('Canal de alertas cifradas habilitado'),
          ),
        ],
      ),
    );
  }
}
