import 'package:hive_flutter/hive_flutter.dart';

class LocalStorageService {
  static const String _boxName = 'qrypta_kv';
  Box<dynamic>? _box;

  Future<void> init() async {
    await Hive.initFlutter();
    _box = await Hive.openBox<dynamic>(_boxName);
  }

  Future<void> setValue(String key, dynamic value) async {
    await _ensureReady();
    await _box!.put(key, value);
  }

  Future<T?> getValue<T>(String key) async {
    await _ensureReady();
    return _box!.get(key) as T?;
  }

  Future<void> remove(String key) async {
    await _ensureReady();
    await _box!.delete(key);
  }

  Future<void> _ensureReady() async {
    if (_box != null && _box!.isOpen) {
      return;
    }
    await init();
  }
}
