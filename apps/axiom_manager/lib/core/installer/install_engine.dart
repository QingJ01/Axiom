import 'dart:io';

import 'install_models.dart';
import 'install_policy.dart';

class InstallEngine {
  Future<InstallPlan> plan(InstallConfig config) async {
    final items = <DiffItem>[];
    final sourceRoot = Directory(config.sourceRoot);
    final targetRoot = Directory(config.targetRoot);

    items.addAll(await _planDirectory(sourceRoot, targetRoot, '.agent'));
    items.addAll(await _planDirectory(sourceRoot, targetRoot, '.github'));

    final gitignore = File('${targetRoot.path}/.gitignore');
    if (!gitignore.existsSync()) {
      items.add(
        DiffItem(
          relativePath: '.gitignore',
          action: DiffAction.create,
          reason: 'create with axiom rules',
        ),
      );
    } else {
      items.add(
        DiffItem(
          relativePath: '.gitignore',
          action: DiffAction.update,
          reason: 'ensure axiom rules',
        ),
      );
    }

    items.add(
      DiffItem(
        relativePath: '.agent/config/agent_config.md',
        action: DiffAction.update,
        reason: 'sync active provider',
      ),
    );
    items.add(
      DiffItem(
        relativePath: '.agent/memory/project_decisions.md',
        action: DiffAction.update,
        reason: 'sync selected tech stack profile',
      ),
    );

    return InstallPlan(items: items);
  }

  Future<ApplyResult> apply(
    InstallConfig config, {
    String? failOnRelativePath,
  }) async {
    await plan(config);
    final targetRoot = Directory(config.targetRoot);
    targetRoot.createSync(recursive: true);

    final backupDir = await Directory.systemTemp.createTemp(
      'axiom_manager_backup_',
    );
    final rollbackRecords = <RollbackRecord>[];
    final applied = <String>[];

    try {
      await _applyDirectory(
        config: config,
        relativeRoot: '.agent',
        backupDir: backupDir,
        rollbackRecords: rollbackRecords,
        applied: applied,
        failOnRelativePath: failOnRelativePath,
      );
      await _applyDirectory(
        config: config,
        relativeRoot: '.github',
        backupDir: backupDir,
        rollbackRecords: rollbackRecords,
        applied: applied,
        failOnRelativePath: failOnRelativePath,
      );

      await _ensureGitignore(
        config.targetRoot,
        backupDir,
        rollbackRecords,
        applied,
        failOnRelativePath,
      );
      await _updateProvider(
        config,
        backupDir,
        rollbackRecords,
        applied,
        failOnRelativePath,
      );
      await _healActiveContext(
        config.targetRoot,
        backupDir,
        rollbackRecords,
        applied,
        failOnRelativePath,
      );
      await _updateProjectDecisions(
        config,
        backupDir,
        rollbackRecords,
        applied,
        failOnRelativePath,
      );

      return ApplyResult(
        success: true,
        applied: applied,
        rollbackRecords: rollbackRecords,
      );
    } catch (e) {
      await _rollback(config.targetRoot, rollbackRecords);
      return ApplyResult(
        success: false,
        error: e.toString(),
        applied: applied,
        rollbackRecords: rollbackRecords,
      );
    } finally {
      if (backupDir.existsSync()) {
        await backupDir.delete(recursive: true);
      }
    }
  }

  Future<List<DiffItem>> _planDirectory(
    Directory sourceRoot,
    Directory targetRoot,
    String relativeRoot,
  ) async {
    final sourceDir = Directory('${sourceRoot.path}/$relativeRoot');
    if (!sourceDir.existsSync()) {
      return <DiffItem>[];
    }

    final items = <DiffItem>[];
    await for (final entity in sourceDir.list(
      recursive: true,
      followLinks: false,
    )) {
      if (entity is! File) continue;
      final relativePath = _toRelative(entity.path, sourceRoot.path);
      final targetFile = File('${targetRoot.path}/$relativePath');
      if (!targetFile.existsSync()) {
        items.add(
          DiffItem(relativePath: relativePath, action: DiffAction.create),
        );
      } else {
        final sourceBytes = entity.readAsBytesSync();
        final targetBytes = targetFile.readAsBytesSync();
        final same = _bytesEqual(sourceBytes, targetBytes);
        if (same) {
          items.add(
            DiffItem(relativePath: relativePath, action: DiffAction.skip),
          );
        } else {
          items.add(
            DiffItem(relativePath: relativePath, action: DiffAction.update),
          );
        }
      }
    }
    return items;
  }

  Future<void> _applyDirectory({
    required InstallConfig config,
    required String relativeRoot,
    required Directory backupDir,
    required List<RollbackRecord> rollbackRecords,
    required List<String> applied,
    required String? failOnRelativePath,
  }) async {
    final sourceRoot = Directory(config.sourceRoot);
    final targetRoot = Directory(config.targetRoot);

    final sourceDir = Directory('${sourceRoot.path}/$relativeRoot');
    if (!sourceDir.existsSync()) return;

    await for (final entity in sourceDir.list(
      recursive: true,
      followLinks: false,
    )) {
      if (entity is! File) continue;
      final relativePath = _toRelative(entity.path, sourceRoot.path);
      final targetFile = File('${targetRoot.path}/$relativePath');
      await _backupTargetFile(
        targetFile,
        relativePath,
        backupDir,
        rollbackRecords,
      );

      if (failOnRelativePath == relativePath) {
        throw StateError('Injected failure at $relativePath');
      }

      targetFile.parent.createSync(recursive: true);
      targetFile.writeAsBytesSync(entity.readAsBytesSync());
      applied.add(relativePath);
    }
  }

  Future<void> _ensureGitignore(
    String targetRoot,
    Directory backupDir,
    List<RollbackRecord> rollbackRecords,
    List<String> applied,
    String? failOnRelativePath,
  ) async {
    const relativePath = '.gitignore';
    final file = File('$targetRoot/$relativePath');
    await _backupTargetFile(file, relativePath, backupDir, rollbackRecords);

    if (failOnRelativePath == relativePath) {
      throw StateError('Injected failure at $relativePath');
    }

    final current = file.existsSync() ? file.readAsStringSync() : '';
    final updated = InstallPolicy.ensureGitignoreRules(current);
    file.parent.createSync(recursive: true);
    file.writeAsStringSync(updated.endsWith('\n') ? updated : '$updated\n');
    applied.add(relativePath);
  }

  Future<void> _updateProvider(
    InstallConfig config,
    Directory backupDir,
    List<RollbackRecord> rollbackRecords,
    List<String> applied,
    String? failOnRelativePath,
  ) async {
    const relativePath = '.agent/config/agent_config.md';
    final file = File('${config.targetRoot}/$relativePath');
    await _backupTargetFile(file, relativePath, backupDir, rollbackRecords);

    if (failOnRelativePath == relativePath) {
      throw StateError('Injected failure at $relativePath');
    }

    final current = file.existsSync() ? file.readAsStringSync() : '';
    final updated = InstallPolicy.replaceActiveProvider(
      current,
      config.activeProvider,
    );
    file.parent.createSync(recursive: true);
    file.writeAsStringSync(updated);
    applied.add(relativePath);
  }

  Future<void> _healActiveContext(
    String targetRoot,
    Directory backupDir,
    List<RollbackRecord> rollbackRecords,
    List<String> applied,
    String? failOnRelativePath,
  ) async {
    const relativePath = '.agent/memory/active_context.md';
    final file = File('$targetRoot/$relativePath');
    await _backupTargetFile(file, relativePath, backupDir, rollbackRecords);
    if (failOnRelativePath == relativePath) {
      throw StateError('Injected failure at $relativePath');
    }

    final current = file.existsSync()
        ? file.readAsStringSync()
        : InstallPolicy.defaultActiveContext();
    final updated = InstallPolicy.ensureActiveContextFrontmatter(current);
    file.parent.createSync(recursive: true);
    file.writeAsStringSync(updated);
    applied.add(relativePath);
  }

  Future<void> _updateProjectDecisions(
    InstallConfig config,
    Directory backupDir,
    List<RollbackRecord> rollbackRecords,
    List<String> applied,
    String? failOnRelativePath,
  ) async {
    const relativePath = '.agent/memory/project_decisions.md';
    final file = File('${config.targetRoot}/$relativePath');
    await _backupTargetFile(file, relativePath, backupDir, rollbackRecords);
    if (failOnRelativePath == relativePath) {
      throw StateError('Injected failure at $relativePath');
    }

    final profile =
        (config.techStackId == 'other' && config.customTechStack != null)
            ? config.customTechStack!
            : resolveTechStack(config.techStackId);
    final current = file.existsSync() ? file.readAsStringSync() : '';
    final updated = InstallPolicy.upsertTechStackProfile(
      current,
      sdk: profile.sdk,
      language: profile.language,
      architecture: profile.architecture,
      lint: profile.lint,
      formatting: profile.formatting,
    );

    file.parent.createSync(recursive: true);
    file.writeAsStringSync(updated);
    applied.add(relativePath);
  }

  Future<void> _backupTargetFile(
    File targetFile,
    String relativePath,
    Directory backupDir,
    List<RollbackRecord> rollbackRecords,
  ) async {
    final backupPath = '${backupDir.path}/$relativePath.bak';
    final backupFile = File(backupPath);
    backupFile.parent.createSync(recursive: true);

    if (targetFile.existsSync()) {
      backupFile.writeAsStringSync(targetFile.readAsStringSync());
    } else {
      backupFile.writeAsStringSync('__MISSING__');
    }

    rollbackRecords.add(
      RollbackRecord(relativePath: relativePath, backupPath: backupPath),
    );
  }

  Future<void> _rollback(
    String targetRoot,
    List<RollbackRecord> records,
  ) async {
    for (final record in records.reversed) {
      final targetFile = File('$targetRoot/${record.relativePath}');
      final backupFile = File(record.backupPath);
      if (!backupFile.existsSync()) continue;

      final content = backupFile.readAsStringSync();
      if (content == '__MISSING__') {
        if (targetFile.existsSync()) {
          targetFile.deleteSync();
        }
      } else {
        targetFile.parent.createSync(recursive: true);
        targetFile.writeAsStringSync(content);
      }
    }
  }

  String _toRelative(String fullPath, String rootPath) {
    final normalizedFull = fullPath.replaceAll('\\', '/');
    final normalizedRoot = rootPath.replaceAll('\\', '/');
    if (normalizedFull.startsWith('$normalizedRoot/')) {
      return normalizedFull.substring(normalizedRoot.length + 1);
    }
    return normalizedFull;
  }

  bool _bytesEqual(List<int> a, List<int> b) {
    if (a.length != b.length) {
      return false;
    }
    for (var i = 0; i < a.length; i++) {
      if (a[i] != b[i]) {
        return false;
      }
    }
    return true;
  }
}
