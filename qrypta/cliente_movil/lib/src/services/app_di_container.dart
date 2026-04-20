import 'package:qrypta_cliente_flutter/src/services/local_identity_store.dart';
import 'package:qrypta_cliente_flutter/src/services/local_storage_service.dart';
import 'package:qrypta_cliente_flutter/src/services/message_api_service.dart';
import 'package:qrypta_cliente_flutter/src/services/message_cache_service.dart';
import 'package:qrypta_cliente_flutter/src/services/push_notification_service.dart';
import 'package:qrypta_cliente_flutter/src/services/realtime_sync_service.dart';

class AppDiContainer {
  AppDiContainer._();

  static final AppDiContainer instance = AppDiContainer._();

  final LocalIdentityStore identityStore = LocalIdentityStore();
  final LocalStorageService localStorage = LocalStorageService();
  final MessageApiService messageApi = MessageApiService();
  final MessageCacheService messageCache = MessageCacheService();
  final RealtimeSyncService realtimeSync = RealtimeSyncService();
  final PushNotificationService pushNotifications = PushNotificationService();
}
