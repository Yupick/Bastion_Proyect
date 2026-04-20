import 'package:dio/dio.dart';

class IncomingApiMessage {
  const IncomingApiMessage({
    required this.peerIdOrigen,
    required this.payloadCifradoB64,
    required this.firmaB64,
    required this.timestamp,
  });

  final String peerIdOrigen;
  final String payloadCifradoB64;
  final String firmaB64;
  final DateTime timestamp;
}

class MessageApiService {
  MessageApiService({Dio? client}) : _client = client ?? Dio() {
    _client.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          options.headers['Content-Type'] = 'application/json';
          handler.next(options);
        },
      ),
    );
  }

  final Dio _client;

  Future<void> sendMessage({
    required String serverBaseUrl,
    required String peerIdOrigen,
    required String peerIdDestino,
    required String payloadCifradoB64,
    required String firmaB64,
  }) async {
    final uri = Uri.parse('$serverBaseUrl/v1/mensaje');
    final response = await _client.postUri(
      uri,
      data: <String, dynamic>{
        'peerIdOrigen': peerIdOrigen,
        'peerIdDestino': peerIdDestino,
        'payloadCifradoB64': payloadCifradoB64,
        'timestamp': DateTime.now().toUtc().toIso8601String(),
        'firmaB64': firmaB64,
      },
    );

    if ((response.statusCode ?? 500) >= 400) {
      throw Exception('Error enviando mensaje (${response.statusCode})');
    }
  }

  Future<List<IncomingApiMessage>> fetchMessages({
    required String serverBaseUrl,
    required String peerId,
  }) async {
    final uri = Uri.parse('$serverBaseUrl/v1/mensajes/$peerId');
    final response = await _client.getUri(uri);
    if ((response.statusCode ?? 500) >= 400) {
      throw Exception('Error consultando mensajes (${response.statusCode})');
    }

    final data = (response.data as List<dynamic>).cast<Map<String, dynamic>>();

    return data
        .map(
          (e) => IncomingApiMessage(
            peerIdOrigen: e['peerIdOrigen'] as String,
            payloadCifradoB64: e['payloadCifradoB64'] as String,
            firmaB64: e['firmaB64'] as String,
            timestamp: DateTime.parse(e['timestamp'] as String),
          ),
        )
        .toList();
  }

  Future<void> createGroup({
    required String serverBaseUrl,
    required String groupId,
    required String adminPeerId,
    required List<String> members,
    required String groupKey,
  }) async {
    final uri = Uri.parse('$serverBaseUrl/v1/grupos/crear');
    final response = await _client.postUri(
      uri,
      data: <String, dynamic>{
        'grupo_id': groupId,
        'admin': adminPeerId,
        'miembros': members,
        'clave_grupo': groupKey,
      },
    );
    if ((response.statusCode ?? 500) >= 400) {
      throw Exception('Error creando grupo (${response.statusCode})');
    }
  }

  Future<void> sendGroupMessage({
    required String serverBaseUrl,
    required String groupId,
    required String senderPeerId,
    required String encryptedPayload,
  }) async {
    final uri = Uri.parse('$serverBaseUrl/v1/grupos/mensaje');
    final response = await _client.postUri(
      uri,
      data: <String, dynamic>{
        'grupo_id': groupId,
        'remitente': senderPeerId,
        'payload_cifrado': encryptedPayload,
      },
    );
    if ((response.statusCode ?? 500) >= 400) {
      throw Exception('Error enviando mensaje de grupo (${response.statusCode})');
    }
  }

  Future<List<Map<String, dynamic>>> fetchGroupMessages({
    required String serverBaseUrl,
    required String groupId,
  }) async {
    final uri = Uri.parse('$serverBaseUrl/v1/grupos/$groupId/mensajes');
    final response = await _client.getUri(uri);
    if ((response.statusCode ?? 500) >= 400) {
      throw Exception('Error leyendo grupo (${response.statusCode})');
    }
    return (response.data as List<dynamic>).cast<Map<String, dynamic>>();
  }

  Future<void> updatePresence({
    required String serverBaseUrl,
    required String peerId,
    required bool online,
  }) async {
    final uri = Uri.parse('$serverBaseUrl/v1/presencia/actualizar/$peerId?online=$online');
    final response = await _client.postUri(uri);
    if ((response.statusCode ?? 500) >= 400) {
      throw Exception('Error actualizando presencia (${response.statusCode})');
    }
  }

  Future<bool> getPresence({
    required String serverBaseUrl,
    required String peerId,
  }) async {
    final uri = Uri.parse('$serverBaseUrl/v1/presencia/$peerId');
    final response = await _client.getUri(uri);
    if ((response.statusCode ?? 500) >= 400) {
      throw Exception('Error consultando presencia (${response.statusCode})');
    }
    final map = response.data as Map<String, dynamic>;
    return map['online'] as bool? ?? false;
  }

  Future<void> registerPushToken({
    required String serverBaseUrl,
    required String peerId,
    required String token,
  }) async {
    final uri = Uri.parse('$serverBaseUrl/v1/push/registrar');
    final response = await _client.postUri(
      uri,
      data: <String, dynamic>{'peer_id': peerId, 'token_push': token},
    );
    if ((response.statusCode ?? 500) >= 400) {
      throw Exception('Error registrando push (${response.statusCode})');
    }
  }

  Future<void> unregisterPushToken({
    required String serverBaseUrl,
    required String peerId,
  }) async {
    final uri = Uri.parse('$serverBaseUrl/v1/push/baja');
    final response = await _client.postUri(
      uri,
      data: <String, dynamic>{'peer_id': peerId},
    );
    if ((response.statusCode ?? 500) >= 400) {
      throw Exception('Error dando de baja push (${response.statusCode})');
    }
  }
}
