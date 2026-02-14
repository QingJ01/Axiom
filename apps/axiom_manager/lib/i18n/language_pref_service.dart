import 'package:axiom_manager/i18n/app_language.dart';
import 'package:shared_preferences/shared_preferences.dart';

class LanguagePrefService {
  static const _key = 'app_language';

  Future<AppLanguage> load({required String systemLanguageCode}) async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString(_key);
    if (saved != null && saved.isNotEmpty) {
      return appLanguageFromString(saved);
    }

    final normalized = systemLanguageCode.toLowerCase();
    if (normalized.startsWith('zh')) {
      return AppLanguage.zh;
    }
    return AppLanguage.en;
  }

  Future<void> save(AppLanguage language) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, appLanguageToString(language));
  }
}
