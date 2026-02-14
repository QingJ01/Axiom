import 'dart:io';

class DoctorReport {
  DoctorReport({required this.errors, required this.warnings});

  final List<String> errors;
  final List<String> warnings;

  bool get ok => errors.isEmpty;
}

class DoctorService {
  Future<DoctorReport> check(String projectRoot) async {
    final errors = <String>[];
    final warnings = <String>[];

    final root = Directory(projectRoot);
    if (!root.existsSync()) {
      return DoctorReport(errors: <String>['目标目录不存在'], warnings: warnings);
    }

    final requiredFiles = <String>[
      '.agent/memory/project_decisions.md',
      '.agent/memory/active_context.md',
      '.agent/config/agent_config.md',
      '.agent/workflows/start.md',
      '.agent/workflows/status.md',
    ];

    for (final rel in requiredFiles) {
      final file = File('$projectRoot/$rel');
      if (!file.existsSync()) {
        errors.add('缺失文件: $rel');
      }
    }

    final contextFile = File('$projectRoot/.agent/memory/active_context.md');
    if (contextFile.existsSync()) {
      final content = contextFile.readAsStringSync();
      final requiredFields = <String>[
        'session_id:',
        'task_status:',
        'auto_fix_attempts:',
        'last_checkpoint:',
      ];
      for (final field in requiredFields) {
        if (!content.contains(field)) {
          errors.add('active_context 缺字段: $field');
        }
      }
    }

    final configFile = File('$projectRoot/.agent/config/agent_config.md');
    if (configFile.existsSync()) {
      final content = configFile.readAsStringSync();
      if (!content.contains('ACTIVE_PROVIDER:')) {
        errors.add('agent_config.md 缺少 ACTIVE_PROVIDER');
      }
    }

    final preCommit = File('$projectRoot/.git/hooks/pre-commit');
    final postCommit = File('$projectRoot/.git/hooks/post-commit');
    if (!preCommit.existsSync()) {
      warnings.add('未安装 pre-commit hook');
    }
    if (!postCommit.existsSync()) {
      warnings.add('未安装 post-commit hook');
    }

    return DoctorReport(errors: errors, warnings: warnings);
  }
}
