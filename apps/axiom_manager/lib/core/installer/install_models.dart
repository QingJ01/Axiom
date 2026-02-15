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
    required this.techStackId,
    this.customTechStack,
  });

  final String sourceRoot;
  final String targetRoot;
  final String activeProvider;
  final String techStackId;
  final TechStackProfile? customTechStack;
}

class TechStackProfile {
  const TechStackProfile({
    required this.id,
    required this.display,
    required this.sdk,
    required this.language,
    required this.architecture,
    required this.lint,
    required this.formatting,
  });

  final String id;
  final String display;
  final String sdk;
  final String language;
  final String architecture;
  final String lint;
  final String formatting;
}

const Map<String, TechStackProfile> kTechStacks = {
  'flutter': TechStackProfile(
    id: 'flutter',
    display: 'Flutter / Dart',
    sdk: 'Flutter',
    language: 'Dart',
    architecture: 'MVVM',
    lint: 'flutter_lints',
    formatting: 'dart format',
  ),
  'react': TechStackProfile(
    id: 'react',
    display: 'React / TypeScript',
    sdk: 'React',
    language: 'TypeScript',
    architecture: 'Component',
    lint: 'eslint',
    formatting: 'prettier',
  ),
  'vue': TechStackProfile(
    id: 'vue',
    display: 'Vue / TypeScript',
    sdk: 'Vue',
    language: 'TypeScript',
    architecture: 'Composition API',
    lint: 'eslint',
    formatting: 'prettier',
  ),
  'django': TechStackProfile(
    id: 'django',
    display: 'Python / Django',
    sdk: 'Django',
    language: 'Python',
    architecture: 'MTV',
    lint: 'flake8',
    formatting: 'black',
  ),
  'node': TechStackProfile(
    id: 'node',
    display: 'Node.js / Express',
    sdk: 'Node.js',
    language: 'JavaScript',
    architecture: 'Layered',
    lint: 'eslint',
    formatting: 'prettier',
  ),
  'other': TechStackProfile(
    id: 'other',
    display: 'Other / Custom',
    sdk: 'Custom',
    language: 'Custom',
    architecture: 'Custom',
    lint: 'N/A',
    formatting: 'N/A',
  ),
};

TechStackProfile resolveTechStack(String id) {
  return kTechStacks[id] ?? kTechStacks['flutter']!;
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
