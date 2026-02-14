import 'package:flutter_test/flutter_test.dart';

import 'package:axiom_manager/main.dart';

void main() {
  testWidgets('wizard should render source sync and directory picker actions', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MyApp());

    expect(find.text('AXIOM MANAGER'), findsOneWidget);
    expect(find.text('Axiom Source Path'), findsOneWidget);
    expect(find.text('Target Directory'), findsOneWidget);
    expect(find.text('Preview Changes'), findsOneWidget);
    expect(find.text('Inject / Apply'), findsOneWidget);
    expect(find.text('Health Check'), findsOneWidget);
  });

  testWidgets('provider list should hide legacy options by default', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MyApp());

    await tester.tap(find.text('gemini_cli').first);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 200));

    expect(find.text('gemini'), findsNothing);
    expect(find.text('claude'), findsNothing);

    await tester.tap(find.text('opencode').last);
    await tester.pumpAndSettle();

    expect(find.text('opencode'), findsWidgets);
  });
}
