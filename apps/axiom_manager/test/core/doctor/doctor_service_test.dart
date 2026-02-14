import 'dart:io';

import 'package:axiom_manager/core/doctor/doctor_service.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('DoctorService', () {
    late Directory sandbox;
    late Directory projectDir;

    setUp(() async {
      sandbox = await Directory.systemTemp.createTemp('axiom_doctor_test_');
      projectDir = Directory('${sandbox.path}/project')
        ..createSync(recursive: true);

      Directory('${projectDir.path}/.agent/memory').createSync(recursive: true);
      File(
        '${projectDir.path}/.agent/memory/project_decisions.md',
      ).writeAsStringSync('# ok');
      File(
        '${projectDir.path}/.agent/memory/active_context.md',
      ).writeAsStringSync('''---
session_id: null
task_status: IDLE
auto_fix_attempts: 0
last_checkpoint: null
---
''');
      Directory('${projectDir.path}/.agent/config').createSync(recursive: true);
      File(
        '${projectDir.path}/.agent/config/agent_config.md',
      ).writeAsStringSync('ACTIVE_PROVIDER: gemini_cli\n');
      Directory(
        '${projectDir.path}/.agent/workflows',
      ).createSync(recursive: true);
      File(
        '${projectDir.path}/.agent/workflows/start.md',
      ).writeAsStringSync('# start');
      File(
        '${projectDir.path}/.agent/workflows/status.md',
      ).writeAsStringSync('# status');

      Directory('${projectDir.path}/.git/hooks').createSync(recursive: true);
      File(
        '${projectDir.path}/.git/hooks/pre-commit',
      ).writeAsStringSync('#!/bin/sh\n');
      File(
        '${projectDir.path}/.git/hooks/post-commit',
      ).writeAsStringSync('#!/bin/sh\n');
    });

    tearDown(() async {
      if (sandbox.existsSync()) {
        await sandbox.delete(recursive: true);
      }
    });

    test('health check should pass for complete project', () async {
      final report = await DoctorService().check(projectDir.path);
      expect(report.ok, isTrue);
      expect(report.errors, isEmpty);
    });

    test('health check should report missing workflow', () async {
      File('${projectDir.path}/.agent/workflows/status.md').deleteSync();

      final report = await DoctorService().check(projectDir.path);
      expect(report.ok, isFalse);
      expect(report.errors.any((e) => e.contains('status.md')), isTrue);
    });
  });
}
