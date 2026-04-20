import 'package:flutter/material.dart';

class ContactsScreen extends StatelessWidget {
  const ContactsScreen({super.key, required this.contacts});

  final List<String> contacts;

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    final isTablet = width >= 700;

    return Scaffold(
      appBar: AppBar(title: const Text('Contactos')),
      body: isTablet
          ? GridView.builder(
              padding: const EdgeInsets.all(16),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                childAspectRatio: 2.8,
              ),
              itemCount: contacts.length,
              itemBuilder: (context, index) {
                return Card(
                  child: ListTile(
                    leading: const Icon(Icons.verified_user_outlined),
                    title: Text(contacts[index]),
                    subtitle: const Text('Alias verificado'),
                  ),
                );
              },
            )
          : ListView.separated(
              itemCount: contacts.length,
              separatorBuilder: (context, index) => const Divider(height: 1),
              itemBuilder: (context, index) {
                return ListTile(
                  leading: const Icon(Icons.verified_user_outlined),
                  title: Text(contacts[index]),
                  subtitle: const Text('Alias verificado'),
                );
              },
            ),
    );
  }
}
