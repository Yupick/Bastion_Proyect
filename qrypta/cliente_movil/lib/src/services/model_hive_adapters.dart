import 'package:hive/hive.dart';
import 'package:qrypta_cliente_flutter/src/models/chat_message.dart';
import 'package:qrypta_cliente_flutter/src/models/identity.dart';

class LocalIdentityAdapter extends TypeAdapter<LocalIdentity> {
  @override
  final int typeId = 10;

  @override
  LocalIdentity read(BinaryReader reader) {
    return LocalIdentity(
      peerId: reader.readString(),
      publicKeyB64: reader.readString(),
      privateKeyB64: reader.readString(),
      mnemonic: reader.readString(),
    );
  }

  @override
  void write(BinaryWriter writer, LocalIdentity obj) {
    writer.writeString(obj.peerId);
    writer.writeString(obj.publicKeyB64);
    writer.writeString(obj.privateKeyB64);
    writer.writeString(obj.mnemonic);
  }
}

class ChatMessageAdapter extends TypeAdapter<ChatMessage> {
  @override
  final int typeId = 11;

  @override
  ChatMessage read(BinaryReader reader) {
    return ChatMessage(
      from: reader.readString(),
      body: reader.readString(),
      timestamp: DateTime.parse(reader.readString()),
      incoming: reader.readBool(),
    );
  }

  @override
  void write(BinaryWriter writer, ChatMessage obj) {
    writer.writeString(obj.from);
    writer.writeString(obj.body);
    writer.writeString(obj.timestamp.toUtc().toIso8601String());
    writer.writeBool(obj.incoming);
  }
}

void registerHiveAdapters() {
  if (!Hive.isAdapterRegistered(10)) {
    Hive.registerAdapter(LocalIdentityAdapter());
  }
  if (!Hive.isAdapterRegistered(11)) {
    Hive.registerAdapter(ChatMessageAdapter());
  }
}
