enum AppLanguage { zh, en }

AppLanguage appLanguageFromString(String value) {
  switch (value) {
    case 'zh':
      return AppLanguage.zh;
    case 'en':
      return AppLanguage.en;
    default:
      return AppLanguage.en;
  }
}

String appLanguageToString(AppLanguage language) {
  return language == AppLanguage.zh ? 'zh' : 'en';
}
