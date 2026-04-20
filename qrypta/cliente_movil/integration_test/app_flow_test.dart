import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:qrypta_cliente_flutter/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('flujo onboarding crea identidad y entra al chat', (tester) async {
    app.main();
    await tester.pumpAndSettle(const Duration(seconds: 3));

    final createButton = find.text('Crear identidad nueva');
    if (createButton.evaluate().isNotEmpty) {
      await tester.tap(createButton);
      await tester.pumpAndSettle(const Duration(seconds: 5));
    }

    expect(find.text('Qrypta Mobile MVP'), findsOneWidget);
    expect(find.text('Mensajeria directa E2E'), findsOneWidget);
  });
}
