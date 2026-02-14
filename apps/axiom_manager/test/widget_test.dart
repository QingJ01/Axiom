import 'package:flutter_test/flutter_test.dart';

import 'package:axiom_manager/main.dart';

void main() {
  testWidgets('wizard should render install actions', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MyApp());

    expect(find.text('Axiom Manager'), findsOneWidget);
    expect(find.text('目标项目目录'), findsOneWidget);
    expect(find.text('预览变更'), findsOneWidget);
    expect(find.text('执行导入'), findsOneWidget);
    expect(find.text('健康检查'), findsOneWidget);
  });

  testWidgets('provider dropdown should be changeable', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MyApp());

    await tester.tap(find.text('gemini_cli'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 200));

    await tester.tap(find.text('opencode').last);
    await tester.pumpAndSettle();

    expect(find.text('opencode'), findsWidgets);
  });
}
