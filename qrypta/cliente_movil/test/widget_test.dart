import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:qrypta_cliente_flutter/src/qrypta_app.dart';

void main() {
  testWidgets('Qrypta app starts', (WidgetTester tester) async {
    await tester.pumpWidget(const QryptaApp());
    await tester.pump(const Duration(milliseconds: 200));

    expect(find.byType(Directionality), findsWidgets);
  });
}
