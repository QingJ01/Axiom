import 'package:axiom_manager/core/installer/install_policy.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('InstallPolicy', () {
    test('ensureGitignoreRules should append missing rules only once', () {
      const input = '# existing\nnode_modules/\n';
      final once = InstallPolicy.ensureGitignoreRules(input);
      final twice = InstallPolicy.ensureGitignoreRules(once);

      expect(once.contains('.agent/memory/active_context.md'), isTrue);
      expect(once, twice);
    });

    test('replaceActiveProvider should update existing value', () {
      const cfg = 'ACTIVE_PROVIDER: gemini\nother: x\n';
      final updated = InstallPolicy.replaceActiveProvider(cfg, 'claude_code');

      expect(updated.contains('ACTIVE_PROVIDER: claude_code'), isTrue);
      expect(updated.contains('ACTIVE_PROVIDER: gemini'), isFalse);
    });
  });
}
