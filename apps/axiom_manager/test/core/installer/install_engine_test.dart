import 'dart:io';

import 'package:axiom_manager/core/installer/install_engine.dart';
import 'package:axiom_manager/core/installer/install_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('InstallEngine plan/apply', () {
    late Directory sandbox;
    late Directory sourceDir;
    late Directory targetDir;
    late InstallEngine engine;

    setUp(() async {
      sandbox = await Directory.systemTemp.createTemp('axiom_manager_test_');
      sourceDir = Directory('${sandbox.path}/source')
        ..createSync(recursive: true);
      targetDir = Directory('${sandbox.path}/target')
        ..createSync(recursive: true);

      Directory('${sourceDir.path}/.agent/memory').createSync(recursive: true);
      File(
        '${sourceDir.path}/.agent/memory/project_decisions.md',
      ).writeAsStringSync('# decisions');
      File(
        '${sourceDir.path}/.agent/memory/active_context.md',
      ).writeAsStringSync('''---
task_status: IDLE
---
''');
      Directory('${sourceDir.path}/.agent/config').createSync(recursive: true);
      File(
        '${sourceDir.path}/.agent/config/agent_config.md',
      ).writeAsStringSync('ACTIVE_PROVIDER: gemini\n');

      Directory('${sourceDir.path}/.github').createSync(recursive: true);
      File('${sourceDir.path}/.github/prompts.md').writeAsStringSync('prompt');

      engine = InstallEngine();
    });

    tearDown(() async {
      if (sandbox.existsSync()) {
        await sandbox.delete(recursive: true);
      }
    });

    test('plan should include create actions for missing files', () async {
      final plan = await engine.plan(
        InstallConfig(
          sourceRoot: sourceDir.path,
          targetRoot: targetDir.path,
          activeProvider: 'gemini_cli',
        ),
      );

      expect(
        plan.items.any(
          (i) => i.relativePath == '.agent/memory/project_decisions.md',
        ),
        isTrue,
      );
      expect(plan.items.any((i) => i.action == DiffAction.create), isTrue);
    });

    test('apply should copy files and write active provider', () async {
      final result = await engine.apply(
        InstallConfig(
          sourceRoot: sourceDir.path,
          targetRoot: targetDir.path,
          activeProvider: 'opencode',
        ),
      );

      expect(result.success, isTrue);
      expect(
        File(
          '${targetDir.path}/.agent/memory/project_decisions.md',
        ).existsSync(),
        isTrue,
      );
      final configText =
          File(
            '${targetDir.path}/.agent/config/agent_config.md',
          ).readAsStringSync();
      expect(configText.contains('ACTIVE_PROVIDER: opencode'), isTrue);
    });

    test('apply should rollback on write failure', () async {
      final existing = Directory('${targetDir.path}/.agent/memory')
        ..createSync(recursive: true);
      File('${existing.path}/project_decisions.md').writeAsStringSync('old');

      final result = await engine.apply(
        InstallConfig(
          sourceRoot: sourceDir.path,
          targetRoot: targetDir.path,
          activeProvider: 'gemini_cli',
        ),
        failOnRelativePath: '.agent/memory/active_context.md',
      );

      expect(result.success, isFalse);
      final restored =
          File(
            '${targetDir.path}/.agent/memory/project_decisions.md',
          ).readAsStringSync();
      expect(restored, 'old');
    });
  });
}
