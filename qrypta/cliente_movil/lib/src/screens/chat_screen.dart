import 'package:flutter/material.dart';
import 'package:qrypta_cliente_flutter/config/app_config.dart';
import 'package:qrypta_cliente_flutter/src/models/chat_message.dart';
import 'package:qrypta_cliente_flutter/src/models/identity.dart';
import 'package:qrypta_cliente_flutter/src/screens/contacts_screen.dart';
import 'package:qrypta_cliente_flutter/src/screens/login_screen.dart';
import 'package:qrypta_cliente_flutter/src/screens/recovery_backup_screen.dart';
import 'package:qrypta_cliente_flutter/src/screens/settings_screen.dart';
import 'package:qrypta_cliente_flutter/src/services/backup_service.dart';
import 'package:qrypta_cliente_flutter/src/services/e2e_service.dart';
import 'package:qrypta_cliente_flutter/src/services/identity_service.dart';
import 'package:qrypta_cliente_flutter/src/services/local_identity_store.dart';
import 'package:qrypta_cliente_flutter/src/services/message_api_service.dart';
import 'package:qrypta_cliente_flutter/src/services/message_cache_service.dart';
import 'package:qrypta_cliente_flutter/src/services/realtime_sync_service.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({
    super.key,
    required this.identity,
    required this.onReset,
  });

  final LocalIdentity identity;
  final VoidCallback onReset;

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _serverCtrl = TextEditingController(text: AppConfig.defaultApiBaseUrl);
  final TextEditingController _peerCtrl = TextEditingController();
  final TextEditingController _msgCtrl = TextEditingController();
  final TextEditingController _presencePeerCtrl = TextEditingController();
  final TextEditingController _pushTokenCtrl = TextEditingController();

  final TextEditingController _groupIdCtrl = TextEditingController();
  final TextEditingController _groupMembersCtrl = TextEditingController();
  final TextEditingController _groupMsgCtrl = TextEditingController();

  final TextEditingController _backupPassCtrl = TextEditingController();
  final TextEditingController _backupBlobCtrl = TextEditingController();

  final MessageApiService _api = MessageApiService();
  final E2eService _e2e = E2eService();
  final LocalIdentityStore _store = LocalIdentityStore();
  final BackupService _backupService = BackupService();
  final MessageCacheService _cache = MessageCacheService();
  final RealtimeSyncService _realtime = RealtimeSyncService();

  final List<ChatMessage> _messages = <ChatMessage>[];
  final List<String> _groupMessages = <String>[];
  bool _busy = false;
  String? _status;

  @override
  void initState() {
    super.initState();
    _loadCachedMessages();
    _connectRealtime();
  }

  @override
  void dispose() {
    _realtime.disconnect();
    super.dispose();
  }

  Future<void> _loadCachedMessages() async {
    final cached = await _cache.recent(limit: 25);
    if (!mounted || cached.isEmpty) {
      return;
    }
    setState(() {
      _messages
        ..clear()
        ..addAll(cached);
    });
  }

  void _connectRealtime() {
    _realtime
        .connect(
          wsUrl:
              '${_serverCtrl.text.trim().replaceFirst('http://', 'ws://').replaceFirst('https://', 'wss://')}/ws',
          peerId: widget.identity.peerId,
        )
        .listen((event) {
      if (!mounted) {
        return;
      }

      final raw = event['raw']?.toString();
      final error = event['error']?.toString();
      if (error != null) {
        setState(() => _status = error);
        return;
      }
      if (raw != null) {
        setState(() => _status = 'Realtime: $raw');
      }
    });
  }

  Future<void> _send() async {
    final destination = _peerCtrl.text.trim();
    final message = _msgCtrl.text.trim();
    if (destination.length != 64 || message.isEmpty) {
      setState(() => _status = 'Destino invalido o mensaje vacio');
      return;
    }

    setState(() {
      _busy = true;
      _status = null;
    });

    try {
      final envelope = await _e2e.encryptAndSign(
        local: widget.identity,
        destinationPeerId: destination,
        clearText: message,
      );

      await _api.sendMessage(
        serverBaseUrl: _serverCtrl.text.trim(),
        peerIdOrigen: widget.identity.peerId,
        peerIdDestino: destination,
        payloadCifradoB64: envelope.$1,
        firmaB64: envelope.$2,
      );

      final sent = ChatMessage(
        from: widget.identity.peerId,
        body: message,
        timestamp: DateTime.now(),
        incoming: false,
      );
      await _cache.insert(sent);

      setState(() {
        _messages.insert(0, sent);
        _msgCtrl.clear();
        _status = 'Mensaje enviado';
      });
    } catch (e) {
      setState(() => _status = 'Error enviando: $e');
    } finally {
      setState(() => _busy = false);
    }
  }

  Future<void> _sync() async {
    setState(() {
      _busy = true;
      _status = null;
    });

    try {
      final incoming = await _api.fetchMessages(
        serverBaseUrl: _serverCtrl.text.trim(),
        peerId: widget.identity.peerId,
      );

      for (final item in incoming) {
        final decrypted = await _e2e.decryptIncoming(
          myPeerId: widget.identity.peerId,
          payloadB64: item.payloadCifradoB64,
          peerIdOrigen: item.peerIdOrigen,
        );

        final msg = ChatMessage(
          from: decrypted.senderPeerId,
          body: decrypted.message,
          timestamp: item.timestamp,
          incoming: true,
        );
        await _cache.insert(msg);
        _messages.insert(0, msg);
      }

      setState(() => _status = 'Sincronizado: ${incoming.length} mensaje(s)');
    } catch (e) {
      setState(() => _status = 'Error sincronizando: $e');
    } finally {
      setState(() => _busy = false);
    }
  }

  Future<void> _createGroup() async {
    final groupId = _groupIdCtrl.text.trim();
    final members = _groupMembersCtrl.text
        .split(',')
        .map((e) => e.trim())
        .where((e) => e.isNotEmpty)
        .toSet()
        .toList();

    if (groupId.isEmpty) {
      setState(() => _status = 'Indica un groupId');
      return;
    }

    if (!members.contains(widget.identity.peerId)) {
      members.add(widget.identity.peerId);
    }

    setState(() => _busy = true);
    try {
      await _api.createGroup(
        serverBaseUrl: _serverCtrl.text.trim(),
        groupId: groupId,
        adminPeerId: widget.identity.peerId,
        members: members,
        groupKey: 'qrypta-group-key-$groupId',
      );
      setState(() => _status = 'Grupo creado');
    } catch (e) {
      setState(() => _status = 'Error creando grupo: $e');
    } finally {
      setState(() => _busy = false);
    }
  }

  Future<void> _sendGroupMessage() async {
    final groupId = _groupIdCtrl.text.trim();
    final msg = _groupMsgCtrl.text.trim();
    if (groupId.isEmpty || msg.isEmpty) {
      setState(() => _status = 'Completa groupId y mensaje de grupo');
      return;
    }

    setState(() => _busy = true);
    try {
      final encrypted = await _e2e.encryptAndSign(
        local: widget.identity,
        destinationPeerId: groupId.padRight(64, '0').substring(0, 64),
        clearText: msg,
      );
      await _api.sendGroupMessage(
        serverBaseUrl: _serverCtrl.text.trim(),
        groupId: groupId,
        senderPeerId: widget.identity.peerId,
        encryptedPayload: encrypted.$1,
      );
      _groupMsgCtrl.clear();
      setState(() => _status = 'Mensaje de grupo enviado');
    } catch (e) {
      setState(() => _status = 'Error grupo: $e');
    } finally {
      setState(() => _busy = false);
    }
  }

  Future<void> _syncGroupMessages() async {
    final groupId = _groupIdCtrl.text.trim();
    if (groupId.isEmpty) {
      setState(() => _status = 'Completa el groupId');
      return;
    }

    setState(() => _busy = true);
    try {
      final raw = await _api.fetchGroupMessages(
        serverBaseUrl: _serverCtrl.text.trim(),
        groupId: groupId,
      );
      _groupMessages
        ..clear()
        ..addAll(raw.map((e) => '${e['remitente']}: ${e['payload']}'));
      setState(() => _status = 'Mensajes de grupo sincronizados (${raw.length})');
    } catch (e) {
      setState(() => _status = 'Error sync grupo: $e');
    } finally {
      setState(() => _busy = false);
    }
  }

  Future<void> _setOnline(bool online) async {
    setState(() => _busy = true);
    try {
      await _api.updatePresence(
        serverBaseUrl: _serverCtrl.text.trim(),
        peerId: widget.identity.peerId,
        online: online,
      );
      setState(() => _status = online ? 'Presencia: online' : 'Presencia: offline');
    } catch (e) {
      setState(() => _status = 'Error presencia: $e');
    } finally {
      setState(() => _busy = false);
    }
  }

  Future<void> _checkPresence() async {
    final target = _presencePeerCtrl.text.trim();
    if (target.length != 64) {
      setState(() => _status = 'Peer de presencia invalido');
      return;
    }

    setState(() => _busy = true);
    try {
      final online = await _api.getPresence(
        serverBaseUrl: _serverCtrl.text.trim(),
        peerId: target,
      );
      setState(() => _status = 'Presencia de peer: ${online ? 'online' : 'offline'}');
    } catch (e) {
      setState(() => _status = 'Error consultando presencia: $e');
    } finally {
      setState(() => _busy = false);
    }
  }

  Future<void> _registerPush() async {
    final token = _pushTokenCtrl.text.trim();
    if (token.isEmpty) {
      setState(() => _status = 'Completa token push');
      return;
    }
    setState(() => _busy = true);
    try {
      await _api.registerPushToken(
        serverBaseUrl: _serverCtrl.text.trim(),
        peerId: widget.identity.peerId,
        token: token,
      );
      setState(() => _status = 'Token push registrado');
    } catch (e) {
      setState(() => _status = 'Error push: $e');
    } finally {
      setState(() => _busy = false);
    }
  }

  Future<void> _unregisterPush() async {
    setState(() => _busy = true);
    try {
      await _api.unregisterPushToken(
        serverBaseUrl: _serverCtrl.text.trim(),
        peerId: widget.identity.peerId,
      );
      setState(() => _status = 'Token push dado de baja');
    } catch (e) {
      setState(() => _status = 'Error baja push: $e');
    } finally {
      setState(() => _busy = false);
    }
  }

  Future<void> _exportBackup() async {
    setState(() => _busy = true);
    try {
      final blob = await _backupService.exportEncrypted(
        identity: widget.identity,
        passphrase: _backupPassCtrl.text.trim(),
      );
      _backupBlobCtrl.text = blob;
      setState(() => _status = 'Backup cifrado generado');
    } catch (e) {
      setState(() => _status = 'Error backup: $e');
    } finally {
      setState(() => _busy = false);
    }
  }

  Future<void> _importBackup() async {
    setState(() => _busy = true);
    try {
      final identity = await _backupService.importEncrypted(
        encryptedBlob: _backupBlobCtrl.text.trim(),
        passphrase: _backupPassCtrl.text.trim(),
      );
      await _store.save(identity);
      setState(() => _status = 'Backup restaurado. Reinicia identidad para cargarlo.');
    } catch (e) {
      setState(() => _status = 'Error restaurando backup: $e');
    } finally {
      setState(() => _busy = false);
    }
  }

  Future<void> _resetIdentity() async {
    await _store.clear();
    widget.onReset();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Qrypta Mobile MVP'),
        actions: [
          IconButton(
            onPressed: _busy ? null : _sync,
            icon: const Icon(Icons.sync),
            tooltip: 'Sincronizar',
          ),
          PopupMenuButton<String>(
            onSelected: (value) {
              if (value == 'contactos') {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => ContactsScreen(
                      contacts: _messages.map((e) => e.from).toSet().toList(growable: false),
                    ),
                  ),
                );
              } else if (value == 'ajustes') {
                Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const SettingsScreen()),
                );
              } else if (value == 'backup') {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => RecoveryBackupScreen(
                      backupService: _backupService,
                      identityStore: _store,
                    ),
                  ),
                );
              } else if (value == 'login') {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => LoginScreen(identityService: IdentityService()),
                  ),
                );
              }
            },
            itemBuilder: (_) => const [
              PopupMenuItem(value: 'contactos', child: Text('Contactos')),
              PopupMenuItem(value: 'ajustes', child: Text('Ajustes')),
              PopupMenuItem(value: 'backup', child: Text('Recuperar backup')),
              PopupMenuItem(value: 'login', child: Text('Login local')),
            ],
          ),
          IconButton(
            onPressed: _busy ? null : _resetIdentity,
            icon: const Icon(Icons.logout),
            tooltip: 'Reiniciar identidad',
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Align(
              alignment: Alignment.centerLeft,
              child: Text('PeerID local: ${widget.identity.peerId.substring(0, 16)}...'),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _serverCtrl,
              decoration: const InputDecoration(
                labelText: 'Servidor API',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 8),
            Expanded(
              child: ListView(
                children: [
                  _buildDirectSection(),
                  const SizedBox(height: 8),
                  _buildGroupSection(),
                  const SizedBox(height: 8),
                  _buildPresenceSection(),
                  const SizedBox(height: 8),
                  _buildBackupSection(),
                  const SizedBox(height: 8),
                  if (_busy) const LinearProgressIndicator(),
                  if (_status != null) Text(_status!),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDirectSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Mensajeria directa E2E', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextField(
              controller: _peerCtrl,
              decoration: const InputDecoration(
                labelText: 'Peer destino (64 hex)',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _msgCtrl,
              minLines: 2,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: 'Mensaje',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _busy ? null : _send,
                    icon: const Icon(Icons.send),
                    label: const Text('Enviar'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _busy ? null : _sync,
                    icon: const Icon(Icons.download),
                    label: const Text('Recibir'),
                  ),
                ),
              ],
            ),
            const Divider(),
            if (_messages.isEmpty)
              const Text('Sin mensajes todavía')
            else
              ..._messages.take(8).map(
                    (msg) => ListTile(
                      dense: true,
                      title: Text(msg.body),
                      subtitle: Text('${msg.incoming ? 'Recibido' : 'Enviado'} - ${msg.from.substring(0, 12)}...'),
                    ),
                  ),
          ],
        ),
      ),
    );
  }

  Widget _buildGroupSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Grupos E2E', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextField(
              controller: _groupIdCtrl,
              decoration: const InputDecoration(
                labelText: 'Group ID',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _groupMembersCtrl,
              decoration: const InputDecoration(
                labelText: 'Miembros (peerIds separados por coma)',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: _busy ? null : _createGroup,
                    child: const Text('Crear grupo'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton(
                    onPressed: _busy ? null : _syncGroupMessages,
                    child: const Text('Sync grupo'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _groupMsgCtrl,
              decoration: const InputDecoration(
                labelText: 'Mensaje de grupo',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 8),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _busy ? null : _sendGroupMessage,
                child: const Text('Enviar mensaje de grupo'),
              ),
            ),
            if (_groupMessages.isNotEmpty)
              ..._groupMessages.take(5).map((m) => Text(m, maxLines: 1, overflow: TextOverflow.ellipsis)),
          ],
        ),
      ),
    );
  }

  Widget _buildPresenceSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Presencia', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: _busy ? null : () => _setOnline(true),
                    child: const Text('Estoy online'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton(
                    onPressed: _busy ? null : () => _setOnline(false),
                    child: const Text('Estoy offline'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _presencePeerCtrl,
              decoration: const InputDecoration(
                labelText: 'Peer para consultar presencia',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _pushTokenCtrl,
              decoration: const InputDecoration(
                labelText: 'Token push local',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: _busy ? null : _checkPresence,
                    child: const Text('Consultar presencia'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _busy ? null : _registerPush,
                    child: const Text('Registrar push'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton(
                    onPressed: _busy ? null : _unregisterPush,
                    child: const Text('Baja push'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBackupSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Backup cifrado', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextField(
              controller: _backupPassCtrl,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'Passphrase backup (min 8)',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: _busy ? null : _exportBackup,
                    child: const Text('Generar backup'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton(
                    onPressed: _busy ? null : _importBackup,
                    child: const Text('Restaurar backup'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _backupBlobCtrl,
              minLines: 3,
              maxLines: 5,
              decoration: const InputDecoration(
                labelText: 'Blob backup cifrado',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
