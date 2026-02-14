import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  group('release scripts', () {
    final root = Directory.current.path;

    test('windows release script should support unsigned and signed mode', () {
      final script = File('$root/tool/release_windows.ps1').readAsStringSync();

      expect(script.contains('ValidateSet("unsigned", "signed")'), isTrue);
      expect(script.contains('dist/windows/\$Mode'), isTrue);
      expect(script.contains('Get-Command flutter'), isTrue);
      expect(script.contains('Get-Command git'), isTrue);
      expect(script.contains('flutter build windows --release'), isTrue);
    });

    test('macos release script should support unsigned and signed mode', () {
      final script = File('$root/tool/release_macos.sh').readAsStringSync();

      expect(script.contains('MODE="unsigned"'), isTrue);
      expect(script.contains('allowed: unsigned|signed'), isTrue);
      expect(script.contains('dist/macos/\$MODE'), isTrue);
      expect(script.contains('command -v flutter'), isTrue);
      expect(script.contains('command -v git'), isTrue);
      expect(script.contains('flutter build macos --release'), isTrue);
    });
  });
}
