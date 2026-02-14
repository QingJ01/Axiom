import 'dart:io';

import 'package:axiom_manager/core/source/axiom_source_service.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AxiomSourceService', () {
    late Directory sandbox;
    late List<List<String>> commands;

    setUp(() async {
      sandbox = await Directory.systemTemp.createTemp('axiom_source_test_');
      commands = <List<String>>[];
    });

    tearDown(() async {
      if (sandbox.existsSync()) {
        await sandbox.delete(recursive: true);
      }
    });

    test('sync should clone when source does not exist', () async {
      final service = AxiomSourceService(
        appDirResolver: () async => sandbox.path,
        runner: (exe, args, {workingDirectory}) async {
          commands.add([exe, ...args]);
          final sourceDir = Directory('${sandbox.path}/res/axiom');
          sourceDir.createSync(recursive: true);
          return ProcessResult(1, 0, '', '');
        },
      );

      final result = await service.sync();
      expect(result.success, isTrue);
      expect(result.sourcePath.endsWith('res${Platform.pathSeparator}axiom'), isTrue);
      expect(commands.any((c) => c.length >= 3 && c[1] == 'clone'), isTrue);
    });

    test('sync should fetch and reset when source exists', () async {
      final sourceDir = Directory('${sandbox.path}/res/axiom')..createSync(recursive: true);
      File('${sourceDir.path}/README.md').writeAsStringSync('x');
      Directory('${sourceDir.path}/.git').createSync(recursive: true);

      final service = AxiomSourceService(
        appDirResolver: () async => sandbox.path,
        runner: (exe, args, {workingDirectory}) async {
          commands.add([exe, ...args]);
          return ProcessResult(1, 0, '', '');
        },
      );

      final result = await service.sync();
      expect(result.success, isTrue);
      expect(commands.any((c) => c.length >= 2 && c[1] == 'fetch'), isTrue);
      expect(commands.any((c) => c.length >= 3 && c[1] == 'reset'), isTrue);
    });

    test('sync should stop when local repo is dirty and force=false', () async {
      final sourceDir = Directory('${sandbox.path}/res/axiom')..createSync(recursive: true);
      Directory('${sourceDir.path}/.git').createSync(recursive: true);

      final service = AxiomSourceService(
        appDirResolver: () async => sandbox.path,
        runner: (exe, args, {workingDirectory}) async {
          commands.add([exe, ...args]);
          if (args.length >= 2 && args[0] == 'status' && args[1] == '--porcelain') {
            return ProcessResult(1, 0, 'M README.md\n', '');
          }
          return ProcessResult(1, 0, '', '');
        },
      );

      final result = await service.sync();
      expect(result.success, isFalse);
      expect(result.message.contains('本地有未提交改动'), isTrue);
      expect(commands.any((c) => c.length >= 2 && c[1] == 'reset'), isFalse);
    });

    test('resolveSourcePath should fallback when preferred path is not writable', () async {
      final service = AxiomSourceService(
        appDirResolver: () async => '${sandbox.path}/app',
        fallbackDirResolver: () async => '${sandbox.path}/fallback',
        pathWritableChecker: (path) => !path.contains('${sandbox.path}/app'),
        runner: (exe, args, {workingDirectory}) async => ProcessResult(1, 0, '', ''),
      );

      final path = await service.resolveSourcePath();
      expect(path.contains('${sandbox.path}/fallback'), isTrue);
      expect(path.endsWith('res${Platform.pathSeparator}axiom'), isTrue);
    });
  });
}
