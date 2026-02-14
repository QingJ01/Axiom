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

    final agentRoot = Directory('$projectRoot/.agent');
    if (!agentRoot.existsSync()) {
      return DoctorReport(
        errors: <String>[
          '未检测到 .agent 目录。请先执行：同步/更新 Axiom -> 执行导入，然后再做健康检查。',
        ],
        warnings: warnings,
      );
    }

    final requiredFiles = <String>[
      '.agent/memory/project_decisions.md',
      '.agent/memory/active_context.md',
      '.agent/config/agent_config.md',
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

    final workflowsDir = Directory('$projectRoot/.agent/workflows');
    if (!workflowsDir.existsSync()) {
      errors.add('缺失目录: .agent/workflows');
    } else {
      final hasWorkflow = workflowsDir
          .listSync()
          .whereType<File>()
          .any((f) => f.path.toLowerCase().endsWith('.md'));
      if (!hasWorkflow) {
        errors.add('.agent/workflows 中未找到 workflow 文件');
      }

      final statusWorkflow = File('$projectRoot/.agent/workflows/status.md');
      if (!statusWorkflow.existsSync()) {
        warnings.add('建议补充 .agent/workflows/status.md 以支持完整状态检查');
      }
    }

    final gitHooksDir = Directory('$projectRoot/.git/hooks');
    if (!gitHooksDir.existsSync()) {
      warnings.add('当前目录不是 Git 仓库（或未初始化 hooks），已跳过 hook 检查');
    } else {
      final preCommit = File('$projectRoot/.git/hooks/pre-commit');
      final postCommit = File('$projectRoot/.git/hooks/post-commit');
      if (!preCommit.existsSync()) {
        warnings.add('未安装 pre-commit hook');
      }
      if (!postCommit.existsSync()) {
        warnings.add('未安装 post-commit hook');
      }
    }

    return DoctorReport(errors: errors, warnings: warnings);
  }
}
