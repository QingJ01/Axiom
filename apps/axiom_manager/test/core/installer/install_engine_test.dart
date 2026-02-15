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

      final binaryDir = Directory('${sourceDir.path}/.agent/assets')
        ..createSync(recursive: true);
      File('${binaryDir.path}/icon.bin')
          .writeAsBytesSync(const <int>[0, 1, 2, 255]);

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
          techStackId: 'flutter',
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
          techStackId: 'react',
        ),
      );

      expect(result.success, isTrue);
      expect(
        File(
          '${targetDir.path}/.agent/memory/project_decisions.md',
        ).existsSync(),
        isTrue,
      );
      final configText = File(
        '${targetDir.path}/.agent/config/agent_config.md',
      ).readAsStringSync();
      expect(configText.contains('ACTIVE_PROVIDER: opencode'), isTrue);

      final decisionsText = File(
        '${targetDir.path}/.agent/memory/project_decisions.md',
      ).readAsStringSync();
      expect(decisionsText.contains('- SDK: React'), isTrue);
      expect(decisionsText.contains('- Language: TypeScript'), isTrue);
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
          techStackId: 'flutter',
        ),
        failOnRelativePath: '.agent/memory/active_context.md',
      );

      expect(result.success, isFalse);
      final restored = File(
        '${targetDir.path}/.agent/memory/project_decisions.md',
      ).readAsStringSync();
      expect(restored, 'old');
    });

    test('plan should compare binary files safely', () async {
      final targetBinaryDir = Directory('${targetDir.path}/.agent/assets')
        ..createSync(recursive: true);
      File('${targetBinaryDir.path}/icon.bin').writeAsBytesSync(
        const <int>[0, 1, 2, 255],
      );

      final plan = await engine.plan(
        InstallConfig(
          sourceRoot: sourceDir.path,
          targetRoot: targetDir.path,
          activeProvider: 'gemini_cli',
          techStackId: 'flutter',
        ),
      );

      final item = plan.items.firstWhere(
        (i) => i.relativePath == '.agent/assets/icon.bin',
      );
      expect(item.action, DiffAction.skip);
    });

    test('apply should create active_context when source file is missing',
        () async {
      File('${sourceDir.path}/.agent/memory/active_context.md').deleteSync();

      final result = await engine.apply(
        InstallConfig(
          sourceRoot: sourceDir.path,
          targetRoot: targetDir.path,
          activeProvider: 'gemini_cli',
          techStackId: 'flutter',
        ),
      );

      expect(result.success, isTrue);
      final created = File('${targetDir.path}/.agent/memory/active_context.md');
      expect(created.existsSync(), isTrue);
      final text = created.readAsStringSync();
      expect(text.contains('session_id:'), isTrue);
      expect(text.contains('task_status:'), isTrue);
    });

    test('apply should write custom tech stack values for other option',
        () async {
      final result = await engine.apply(
        InstallConfig(
          sourceRoot: sourceDir.path,
          targetRoot: targetDir.path,
          activeProvider: 'opencode',
          techStackId: 'other',
          customTechStack: const TechStackProfile(
            id: 'other',
            display: 'Custom',
            sdk: 'Rust',
            language: 'Rust',
            architecture: 'Hexagonal',
            lint: 'clippy',
            formatting: 'rustfmt',
          ),
        ),
      );

      expect(result.success, isTrue);
      final decisionsText = File(
        '${targetDir.path}/.agent/memory/project_decisions.md',
      ).readAsStringSync();
      expect(decisionsText.contains('- SDK: Rust'), isTrue);
      expect(decisionsText.contains('- Pattern: Hexagonal'), isTrue);
      expect(decisionsText.contains('- Lint: clippy'), isTrue);
    });
  });
}
