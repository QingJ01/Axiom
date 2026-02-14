import 'dart:io';

typedef ProcessRunner = Future<ProcessResult> Function(
  String executable,
  List<String> arguments, {
  String? workingDirectory,
});

class SourceSyncResult {
  SourceSyncResult({
    required this.success,
    required this.sourcePath,
    required this.message,
  });

  final bool success;
  final String sourcePath;
  final String message;
}

class AxiomSourceService {
  AxiomSourceService({
    this.repoUrl = 'https://github.com/QingJ01/Axiom.git',
    this.branch = 'main',
    ProcessRunner? runner,
    Future<String> Function()? appDirResolver,
    Future<String> Function()? fallbackDirResolver,
    bool Function(String path)? pathWritableChecker,
  }) : _runner = runner ?? _defaultRunner,
       _appDirResolver = appDirResolver ?? _defaultAppDirResolver,
       _fallbackDirResolver = fallbackDirResolver ?? _defaultFallbackDirResolver,
       _pathWritableChecker = pathWritableChecker ?? _defaultPathWritableChecker;

  final String repoUrl;
  final String branch;
  final ProcessRunner _runner;
  final Future<String> Function() _appDirResolver;
  final Future<String> Function() _fallbackDirResolver;
  final bool Function(String path) _pathWritableChecker;

  Future<String> resolveSourcePath() async {
    final sep = Platform.pathSeparator;
    final appDir = await _appDirResolver();
    final preferredResDir = '$appDir${sep}res';
    if (_pathWritableChecker(preferredResDir)) {
      return '$preferredResDir${sep}axiom';
    }

    final fallbackDir = await _fallbackDirResolver();
    return '$fallbackDir${sep}res${sep}axiom';
  }

  Future<SourceSyncResult> sync({bool force = false}) async {
    final sourcePath = await resolveSourcePath();
    final sourceDir = Directory(sourcePath);
    final resDir = sourceDir.parent;
    resDir.createSync(recursive: true);

    try {
      final gitDir = Directory('${sourceDir.path}${Platform.pathSeparator}.git');
      if (!sourceDir.existsSync()) {
        await _runGit(<String>['clone', '--branch', branch, repoUrl, sourcePath]);
        return SourceSyncResult(
          success: true,
          sourcePath: sourcePath,
          message: '已拉取 Axiom 到 $sourcePath',
        );
      }

      if (!gitDir.existsSync()) {
        if (!force) {
          return SourceSyncResult(
            success: false,
            sourcePath: sourcePath,
            message: '目标源目录不是 Git 仓库，已停止同步。请清理目录后重试，或使用 force 更新。',
          );
        }
        if (sourceDir.existsSync()) {
          sourceDir.deleteSync(recursive: true);
        }
        await _runGit(<String>['clone', '--branch', branch, repoUrl, sourcePath]);
        return SourceSyncResult(
          success: true,
          sourcePath: sourcePath,
          message: '已拉取 Axiom 到 $sourcePath',
        );
      }

      await _runGit(<String>['fetch', '--all'], workingDirectory: sourcePath);
      final statusResult = await _runner(
        'git',
        <String>['status', '--porcelain'],
        workingDirectory: sourcePath,
      );
      if (statusResult.exitCode != 0) {
        throw StateError('git status failed: ${statusResult.stderr}');
      }

      final dirty = statusResult.stdout.toString().trim().isNotEmpty;
      if (dirty && !force) {
        return SourceSyncResult(
          success: false,
          sourcePath: sourcePath,
          message: '本地有未提交改动，已停止更新。请清理后重试，或使用 force 更新。',
        );
      }
      await _runGit(
        <String>['reset', '--hard', 'origin/$branch'],
        workingDirectory: sourcePath,
      );

      return SourceSyncResult(
        success: true,
        sourcePath: sourcePath,
        message: '已更新 Axiom 到最新 $branch',
      );
    } catch (e) {
      return SourceSyncResult(
        success: false,
        sourcePath: sourcePath,
        message: '同步失败: $e',
      );
    }
  }

  Future<void> _runGit(
    List<String> args, {
    String? workingDirectory,
  }) async {
    final result = await _runner('git', args, workingDirectory: workingDirectory);
    if (result.exitCode != 0) {
      throw StateError('git ${args.join(' ')} failed: ${result.stderr}');
    }
  }

  static Future<String> _defaultAppDirResolver() async {
    final sep = Platform.pathSeparator;
    final cwdPubspec = File('${Directory.current.path}${sep}pubspec.yaml');
    if (cwdPubspec.existsSync()) {
      return Directory.current.path;
    }

    final exeParent = File(Platform.resolvedExecutable).parent;
    if (exeParent.existsSync()) {
      return exeParent.path;
    }
    return Directory.current.path;
  }

  static Future<String> _defaultFallbackDirResolver() async {
    final home = Platform.environment['USERPROFILE'] ??
        Platform.environment['HOME'] ??
        Directory.current.path;
    return '$home${Platform.pathSeparator}.axiom-manager';
  }

  static bool _defaultPathWritableChecker(String path) {
    try {
      final dir = Directory(path);
      dir.createSync(recursive: true);
      final probe = File('${dir.path}${Platform.pathSeparator}.write_probe');
      probe.writeAsStringSync('ok');
      probe.deleteSync();
      return true;
    } catch (_) {
      return false;
    }
  }

  static Future<ProcessResult> _defaultRunner(
    String executable,
    List<String> arguments, {
    String? workingDirectory,
  }) {
    return Process.run(
      executable,
      arguments,
      workingDirectory: workingDirectory,
    );
  }
}
