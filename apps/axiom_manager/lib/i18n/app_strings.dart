import 'package:axiom_manager/i18n/app_language.dart';

class AppStrings {
  AppStrings(this.language);

  final AppLanguage language;

  static const Map<String, String> _en = {
    'appTitle': 'Axiom Manager',
    'headerTitle': 'AXIOM MANAGER',
    'sourcePath': 'Axiom Source Path',
    'targetDirectory': 'Target Directory',
    'preview': 'Preview Changes',
    'apply': 'Inject / Apply',
    'healthCheck': 'Health Check',
    'showLegacy': 'Show Legacy Providers',
    'activeProvider': 'Active Provider',
    'clearConsole': 'Clear Console',
    'syncSource': 'Sync Source',
    'browse': 'Browse...',
    'logReady1': 'Axiom Manager Ready.',
    'logReady2': 'Waiting for user input...',
    'logSyncing': 'Syncing Axiom source...',
    'logTargetRequired': 'Target project directory is empty.',
    'logSourceRequired': 'Axiom Source Path is empty. Please sync.',
    'forceSync': 'Force Update',
    'forceSyncConfirm': 'Force update will discard local changes under /res/axiom. Continue?',
  };

  static const Map<String, String> _zh = {
    'appTitle': 'Axiom 管理器',
    'headerTitle': 'AXIOM 管理器',
    'sourcePath': 'Axiom 源路径',
    'targetDirectory': '目标目录',
    'preview': '预览变更',
    'apply': '执行导入',
    'healthCheck': '健康检查',
    'showLegacy': '显示兼容 Provider',
    'activeProvider': '当前 Provider',
    'clearConsole': '清空终端',
    'syncSource': '同步源仓库',
    'browse': '浏览...',
    'logReady1': 'Axiom 管理器已就绪。',
    'logReady2': '等待用户操作...',
    'logSyncing': '正在同步 Axiom 源...',
    'logTargetRequired': '目标项目目录为空。',
    'logSourceRequired': 'Axiom 源路径为空，请先同步。',
    'forceSync': '强制更新',
    'forceSyncConfirm': '强制更新会丢弃 /res/axiom 下本地改动，是否继续？',
  };

  String t(String key) {
    final table = language == AppLanguage.zh ? _zh : _en;
    return table[key] ?? key;
  }
}
