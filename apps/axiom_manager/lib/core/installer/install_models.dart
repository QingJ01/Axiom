enum DiffAction { create, update, skip }

class DiffItem {
  DiffItem({
    required this.relativePath,
    required this.action,
    this.reason = '',
  });

  final String relativePath;
  final DiffAction action;
  final String reason;
}

class InstallPlan {
  InstallPlan({required this.items, this.warnings = const []});

  final List<DiffItem> items;
  final List<String> warnings;
}

class InstallConfig {
  InstallConfig({
    required this.sourceRoot,
    required this.targetRoot,
    required this.activeProvider,
  });

  final String sourceRoot;
  final String targetRoot;
  final String activeProvider;
}

class RollbackRecord {
  RollbackRecord({required this.relativePath, required this.backupPath});

  final String relativePath;
  final String backupPath;
}

class ApplyResult {
  ApplyResult({
    required this.success,
    this.error,
    this.applied = const [],
    this.rollbackRecords = const [],
  });

  final bool success;
  final String? error;
  final List<String> applied;
  final List<RollbackRecord> rollbackRecords;
}
