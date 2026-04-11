class ChatMessage {
  const ChatMessage({
    required this.from,
    required this.body,
    required this.timestamp,
    required this.incoming,
  });

  final String from;
  final String body;
  final DateTime timestamp;
  final bool incoming;
}
