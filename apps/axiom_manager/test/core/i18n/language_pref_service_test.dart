import 'package:axiom_manager/i18n/app_language.dart';
import 'package:axiom_manager/i18n/language_pref_service.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  group('LanguagePrefService', () {
    test('load should fallback to system language when no saved value',
        () async {
      SharedPreferences.setMockInitialValues(<String, Object>{});
      final service = LanguagePrefService();

      final lang = await service.load(
        systemLanguageCode: 'zh-CN',
      );
      expect(lang, AppLanguage.zh);
    });

    test('save and load should persist selected language', () async {
      SharedPreferences.setMockInitialValues(<String, Object>{});
      final service = LanguagePrefService();

      await service.save(AppLanguage.en);
      final loaded = await service.load(systemLanguageCode: 'zh-CN');
      expect(loaded, AppLanguage.en);
    });
  });
}
