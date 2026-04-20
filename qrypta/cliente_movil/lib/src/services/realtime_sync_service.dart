import 'dart:async';
import 'dart:convert';
import 'dart:io';

class RealtimeSyncService {
  WebSocket? _socket;
  StreamController<Map<String, dynamic>>? _controller;

  Stream<Map<String, dynamic>> connect({
    required String wsUrl,
    required String peerId,
  }) {
    _controller?.close();
    _controller = StreamController<Map<String, dynamic>>.broadcast();

    WebSocket.connect('$wsUrl?peerId=$peerId').then((socket) {
      _socket = socket;
      socket.listen(
        (event) {
          try {
            final parsed = jsonDecode(event.toString()) as Map<String, dynamic>;
            _controller?.add(parsed);
          } catch (_) {
            _controller?.add(<String, dynamic>{'raw': event.toString()});
          }
        },
        onDone: () => _controller?.close(),
        onError: (_) => _controller?.close(),
      );
    }).catchError((_) {
      _controller?.add(<String, dynamic>{'error': 'No se pudo conectar al WS'});
    });

    return _controller!.stream;
  }

  Future<void> send(Map<String, dynamic> payload) async {
    final socket = _socket;
    if (socket == null) {
      return;
    }
    socket.add(jsonEncode(payload));
  }

  Future<void> disconnect() async {
    await _socket?.close();
    await _controller?.close();
    _socket = null;
    _controller = null;
  }
}
