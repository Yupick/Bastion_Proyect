import 'package:flutter/material.dart';

class AppThemeController {
  AppThemeController._();

  static final ValueNotifier<ThemeMode> mode = ValueNotifier<ThemeMode>(ThemeMode.light);

  static void setDarkMode(bool enabled) {
    mode.value = enabled ? ThemeMode.dark : ThemeMode.light;
  }

  static bool get isDarkMode => mode.value == ThemeMode.dark;
}
