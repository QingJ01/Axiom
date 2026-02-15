class InstallPolicy {
  static const List<String> gitignoreRules = <String>[
    '.agent/memory/active_context.md',
    '.agent/memory/history/',
    '.agent/memory/evolution/workflow_metrics.md',
    '.agent/memory/evolution/learning_queue.md',
    '.agent/memory/evolution/reflection_log.md',
    '.agent/memory/evolution/pattern_library.md',
    '.agent/memory/reviews/',
    '.agent/memory/watchdog_status.lock',
    '.agent/memory/*.lock',
    '.agent/**/__pycache__/',
  ];

  static String ensureGitignoreRules(String current) {
    final lines = current.split('\n').map((line) => line.trimRight()).toList();

    final existing = lines.toSet();
    final missing = gitignoreRules.where((r) => !existing.contains(r)).toList();
    if (missing.isEmpty) return lines.join('\n');

    if (lines.isNotEmpty && lines.last.isNotEmpty) {
      lines.add('');
    }
    lines.add('# === Axiom (补充) ===');
    lines.addAll(missing);
    return lines.join('\n');
  }

  static String replaceActiveProvider(String current, String provider) {
    final pattern = RegExp(r'ACTIVE_PROVIDER:\s*[^\n\r]+');
    if (pattern.hasMatch(current)) {
      return current.replaceFirst(pattern, 'ACTIVE_PROVIDER: $provider');
    }
    if (current.isEmpty) {
      return 'ACTIVE_PROVIDER: $provider\n';
    }
    final end = current.endsWith('\n') ? '' : '\n';
    return '$current${end}ACTIVE_PROVIDER: $provider\n';
  }

  static String ensureActiveContextFrontmatter(String content) {
    if (!content.startsWith('---\n')) {
      return content;
    }
    final end = content.indexOf('\n---\n', 4);
    if (end == -1) {
      return content;
    }

    final frontmatter = content.substring(4, end).split('\n');
    final map = <String, String>{};
    for (final line in frontmatter) {
      final idx = line.indexOf(':');
      if (idx <= 0) continue;
      final key = line.substring(0, idx).trim();
      final value = line.substring(idx + 1).trim();
      map[key] = value;
    }

    map.putIfAbsent('session_id', () => 'null');
    map.putIfAbsent('task_status', () => 'IDLE');
    map.putIfAbsent('auto_fix_attempts', () => '0');
    map.putIfAbsent('last_checkpoint', () => 'null');

    final orderedKeys = <String>[
      'session_id',
      'task_status',
      'auto_fix_attempts',
      'last_checkpoint',
    ];

    final merged = <String>[];
    for (final key in orderedKeys) {
      merged.add('$key: ${map[key]}');
      map.remove(key);
    }
    for (final entry in map.entries) {
      merged.add('${entry.key}: ${entry.value}');
    }

    return '---\n${merged.join('\n')}\n---\n${content.substring(end + 5)}';
  }

  static String defaultActiveContext() {
    return '''---
session_id: null
task_status: IDLE
auto_fix_attempts: 0
last_checkpoint: null
---

# Active Context

current_task: null
notes: []
''';
  }

  static String upsertTechStackProfile(
    String content, {
    required String sdk,
    required String language,
    required String architecture,
    required String lint,
    required String formatting,
  }) {
    const startMarker = '<!-- AUTO-GENERATED CONTEXT START -->';
    const endMarker = '<!-- AUTO-GENERATED CONTEXT END -->';

    final block = '''$startMarker
## 📌 项目上下文 (自动同步)

### 技术栈

- SDK: $sdk
- Language: $language

### 架构设计

- Pattern: $architecture

### 编码规范

- Lint: $lint
- Formatting: $formatting
$endMarker''';

    final start = content.indexOf(startMarker);
    final end = content.indexOf(endMarker);
    if (start >= 0 && end > start) {
      final tailStart = end + endMarker.length;
      return '${content.substring(0, start)}$block${content.substring(tailStart)}';
    }

    if (content.trim().isEmpty) {
      return '# Project Decisions\n\n$block\n';
    }

    final sep = content.endsWith('\n') ? '' : '\n';
    return '$content$sep\n$block\n';
  }
}
