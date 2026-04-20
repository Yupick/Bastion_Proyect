import 'package:qrypta_cliente_flutter/src/models/chat_message.dart';
import 'package:sqflite/sqflite.dart';

class MessageCacheService {
  Database? _db;

  Future<void> init() async {
    if (_db != null) {
      return;
    }

    final dbPath = await getDatabasesPath();
    _db = await openDatabase(
      '$dbPath/qrypta_messages.db',
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            body TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            incoming INTEGER NOT NULL
          )
        ''');
      },
    );
  }

  Future<void> insert(ChatMessage message) async {
    await init();
    await _db!.insert(
      'messages',
      <String, dynamic>{
        'sender': message.from,
        'body': message.body,
        'timestamp': message.timestamp.toUtc().toIso8601String(),
        'incoming': message.incoming ? 1 : 0,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<List<ChatMessage>> recent({int limit = 50}) async {
    await init();
    final rows = await _db!.query(
      'messages',
      orderBy: 'id DESC',
      limit: limit,
    );

    return rows
        .map(
          (row) => ChatMessage(
            from: row['sender'] as String,
            body: row['body'] as String,
            timestamp: DateTime.parse(row['timestamp'] as String).toLocal(),
            incoming: (row['incoming'] as int) == 1,
          ),
        )
        .toList();
  }
}
