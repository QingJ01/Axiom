import 'dart:io';

import 'package:axiom_manager/core/doctor/doctor_service.dart';
import 'package:axiom_manager/core/installer/install_engine.dart';
import 'package:axiom_manager/core/installer/install_models.dart';
import 'package:axiom_manager/core/source/axiom_source_service.dart';
import 'package:axiom_manager/i18n/app_language.dart';
import 'package:axiom_manager/i18n/app_strings.dart';
import 'package:axiom_manager/i18n/language_pref_service.dart';
import 'package:axiom_manager/ui/theme.dart';
import 'package:axiom_manager/ui/widgets/app_logo.dart';
import 'package:axiom_manager/ui/widgets/axiom_button.dart';
import 'package:axiom_manager/ui/widgets/glass_container.dart';
import 'package:axiom_manager/ui/widgets/terminal_output.dart';
import 'package:file_selector/file_selector.dart';
import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({
    super.key,
    this.forcedLanguage,
    this.persistLanguage = true,
  });

  final AppLanguage? forcedLanguage;
  final bool persistLanguage;

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  final _prefService = LanguagePrefService();
  AppLanguage _language = AppLanguage.en;
  bool _ready = false;

  @override
  void initState() {
    super.initState();
    _initLanguage();
  }

  Future<void> _initLanguage() async {
    if (widget.forcedLanguage != null) {
      setState(() {
        _language = widget.forcedLanguage!;
        _ready = true;
      });
      return;
    }

    final localeCode =
        WidgetsBinding.instance.platformDispatcher.locale.languageCode;
    final loaded = await _prefService.load(systemLanguageCode: localeCode);
    if (!mounted) return;
    setState(() {
      _language = loaded;
      _ready = true;
    });
  }

  Future<void> _onLanguageChanged(AppLanguage next) async {
    setState(() {
      _language = next;
    });
    if (widget.persistLanguage) {
      await _prefService.save(next);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!_ready) {
      return MaterialApp(
        home: Scaffold(
          body: Center(child: CircularProgressIndicator()),
        ),
      );
    }

    final strings = AppStrings(_language);
    return MaterialApp(
      title: strings.t('appTitle'),
      debugShowCheckedModeBanner: false,
      theme: AxiomTheme.darkTheme,
      home: InstallerHomePage(
        language: _language,
        onLanguageChanged: _onLanguageChanged,
      ),
    );
  }
}

class ProviderOption {
  const ProviderOption(this.id, {this.legacy = false, this.note = ''});

  final String id;
  final bool legacy;
  final String note;
}

class InstallerHomePage extends StatefulWidget {
  const InstallerHomePage({
    super.key,
    required this.language,
    required this.onLanguageChanged,
    this.engine,
    this.doctor,
    this.sourceService,
    this.directoryPicker,
  });

  final AppLanguage language;
  final Future<void> Function(AppLanguage language) onLanguageChanged;

  final InstallEngine? engine;
  final DoctorService? doctor;
  final AxiomSourceService? sourceService;
  final Future<String?> Function()? directoryPicker;

  @override
  State<InstallerHomePage> createState() => _InstallerHomePageState();
}

class _InstallerHomePageState extends State<InstallerHomePage> {
  static const _allProviders = <ProviderOption>[
    ProviderOption('gemini_cli'),
    ProviderOption('claude_code'),
    ProviderOption('codex'),
    ProviderOption('opencode'),
    ProviderOption('copilot'),
    ProviderOption('gemini', legacy: true, note: '兼容旧配置，建议使用 gemini_cli'),
    ProviderOption('claude', legacy: true, note: '兼容旧配置，建议使用 claude_code'),
  ];

  late final InstallEngine _engine;
  late final DoctorService _doctor;
  late final AxiomSourceService _sourceService;
  late final Future<String?> Function() _directoryPicker;

  final _sourceController = TextEditingController();
  final _targetController = TextEditingController();
  final _scrollController = ScrollController();

  String _provider = 'gemini_cli';
  String _techStackId = 'flutter';
  bool _showLegacyProviders = false;
  bool _busy = false;
  String _output = '';

  AppStrings get _strings => AppStrings(widget.language);

  @override
  void initState() {
    super.initState();
    _engine = widget.engine ?? InstallEngine();
    _doctor = widget.doctor ?? DoctorService();
    _sourceService = widget.sourceService ?? AxiomSourceService();
    _directoryPicker = widget.directoryPicker ?? (() => getDirectoryPath());
    _output = _welcomeText();
    _initSourcePath();
  }

  @override
  void dispose() {
    _sourceController.dispose();
    _targetController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  void didUpdateWidget(covariant InstallerHomePage oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.language != widget.language && _output.startsWith('>')) {
      setState(() {
        _output = _welcomeText();
      });
    }
  }

  void _log(String message) {
    setState(() {
      _output += '\n> $message';
    });
    // Scroll to bottom after frame
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _clearLog() {
    setState(() {
      _output = '> Console cleared.';
    });
  }

  String _welcomeText() {
    return '> ${_strings.t('logReady1')}\n> ${_strings.t('logReady2')}';
  }

  @override
  Widget build(BuildContext context) {
    final providerOptions =
        _allProviders.where((p) => _showLegacyProviders || !p.legacy).toList();

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            children: [
              _buildHeader(),
              const SizedBox(height: 16),
              Expanded(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Left Panel: Configuration
                    Expanded(
                      flex: 2,
                      child: GlassContainer(
                        opacity: 0.05,
                        child: SingleChildScrollView(
                          padding: const EdgeInsets.all(24),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              _buildSectionTitle('Source Configuration'),
                              const SizedBox(height: 16),
                              _buildSourceInput(),
                              const SizedBox(height: 24),
                              _buildSectionTitle('Target Project'),
                              const SizedBox(height: 16),
                              _buildTargetInput(),
                              const SizedBox(height: 24),
                              _buildSectionTitle('Tech Stack'),
                              const SizedBox(height: 16),
                              _buildTechStackSelector(),
                              const SizedBox(height: 24),
                              _buildSectionTitle('AI Provider'),
                              const SizedBox(height: 16),
                              _buildProviderSelector(providerOptions),
                              const SizedBox(height: 32),
                              const Divider(color: Colors.white10),
                              const SizedBox(height: 24),
                              _buildActionButtons(),
                            ],
                          ),
                        ),
                      ),
                    ),

                    const SizedBox(width: 24),

                    // Right Panel: Terminal
                    Expanded(
                      flex: 3,
                      child: Column(
                        children: [
                          Expanded(
                            child: TerminalOutput(
                              output: _output,
                              scrollController: _scrollController,
                            ),
                          ),
                          const SizedBox(height: 12),
                          Align(
                            alignment: Alignment.centerRight,
                            child: TextButton.icon(
                              onPressed: _clearLog,
                              icon:
                                  const Icon(Icons.cleaning_services, size: 16),
                              label: Text(_strings.t('clearConsole')),
                              style: TextButton.styleFrom(
                                foregroundColor: AxiomTheme.textSecondary,
                              ),
                            ),
                          )
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        const AppLogo(size: 34),
        const SizedBox(width: 10),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _strings.t('headerTitle'),
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            Text(
              'v1.0.0+1 | System State: ONLINE',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AxiomTheme.accent.withValues(alpha: 0.7),
                    letterSpacing: 1,
                  ),
            ),
          ],
        ),
        const Spacer(),
        OutlinedButton(
          onPressed: _busy
              ? null
              : () {
                  final next = widget.language == AppLanguage.en
                      ? AppLanguage.zh
                      : AppLanguage.en;
                  widget.onLanguageChanged(next);
                },
          child: Text(widget.language == AppLanguage.en ? 'EN' : '中文'),
        ),
      ],
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title.toUpperCase(),
      style: TextStyle(
        fontSize: 12,
        fontWeight: FontWeight.bold,
        color: AxiomTheme.textSecondary,
        letterSpacing: 1.2,
      ),
    );
  }

  Widget _buildSourceInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextField(
          controller: _sourceController,
          readOnly: true,
          decoration: InputDecoration(
            labelText: _strings.t('sourcePath'),
            prefixIcon: const Icon(Icons.folder_shared_outlined),
            suffixIcon: IconButton(
              icon: const Icon(Icons.sync),
              tooltip: _strings.t('syncSource'),
              onPressed: _busy ? null : _syncSource,
            ),
          ),
        ),
        const SizedBox(height: 10),
        Align(
          alignment: Alignment.centerRight,
          child: OutlinedButton.icon(
            onPressed: _busy ? null : _forceSync,
            icon: const Icon(Icons.warning_amber_rounded),
            label: Text(_strings.t('forceSync')),
          ),
        ),
      ],
    );
  }

  Widget _buildTargetInput() {
    return Row(
      children: [
        Expanded(
          child: TextField(
            controller: _targetController,
            decoration: InputDecoration(
              labelText: _strings.t('targetDirectory'),
              prefixIcon: const Icon(Icons.folder_open_outlined),
            ),
          ),
        ),
        const SizedBox(width: 12),
        IconButton.filledTonal(
          onPressed: _busy ? null : _pickTargetDirectory,
          icon: const Icon(Icons.more_horiz),
          tooltip: _strings.t('browse'),
        ),
      ],
    );
  }

  Widget _buildProviderSelector(List<ProviderOption> options) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        DropdownButtonFormField<String>(
          value: _provider,
          isExpanded: true,
          decoration: InputDecoration(
            prefixIcon: const Icon(Icons.psychology),
            labelText: _strings.t('activeProvider'),
          ),
          dropdownColor: AxiomTheme.surface,
          items: options.map((p) {
            return DropdownMenuItem<String>(
              value: p.id,
              child: Text(p.id),
            );
          }).toList(),
          onChanged: _busy
              ? null
              : (value) {
                  if (value == null) return;
                  setState(() {
                    _provider = value;
                    final selected =
                        _allProviders.firstWhere((p) => p.id == value);
                    if (selected.note.isNotEmpty) {
                      _log('[INFO] Provider selected: ${selected.id}');
                      _log('[NOTE] ${selected.note}');
                    } else {
                      _log('[INFO] Provider switched to: ${selected.id}');
                    }
                  });
                },
        ),
        const SizedBox(height: 8),
        CheckboxListTile(
          value: _showLegacyProviders,
          onChanged: _busy
              ? null
              : (value) {
                  setState(() {
                    _showLegacyProviders = value ?? false;
                    if (!_showLegacyProviders &&
                        (_provider == 'gemini' || _provider == 'claude')) {
                      _provider =
                          _provider == 'gemini' ? 'gemini_cli' : 'claude_code';
                      _log(
                          '[WARN] Legacy provider hidden. Auto-switched to $_provider');
                    }
                  });
                },
          title: Text(_strings.t('showLegacy')),
          controlAffinity: ListTileControlAffinity.leading,
          dense: true,
          contentPadding: EdgeInsets.zero,
        ),
      ],
    );
  }

  Widget _buildTechStackSelector() {
    final options = kTechStacks.values.toList();
    return DropdownButtonFormField<String>(
      value: _techStackId,
      isExpanded: true,
      decoration: InputDecoration(
        prefixIcon: const Icon(Icons.integration_instructions_outlined),
        labelText: _strings.t('techStack'),
      ),
      dropdownColor: AxiomTheme.surface,
      items: options
          .map(
            (stack) => DropdownMenuItem<String>(
              value: stack.id,
              child: Text(stack.display),
            ),
          )
          .toList(),
      onChanged: _busy
          ? null
          : (value) {
              if (value == null) {
                return;
              }
              setState(() {
                _techStackId = value;
              });
              _log(
                  '[INFO] Tech stack switched to: ${resolveTechStack(value).display}');
            },
    );
  }

  Widget _buildActionButtons() {
    return Wrap(
      spacing: 12,
      runSpacing: 12,
      children: [
        AxiomButton(
          label: _strings.t('preview'),
          icon: Icons.preview,
          onPressed: _busy ? null : _preview,
          isPrimary: false,
        ),
        AxiomButton(
          label: _strings.t('apply'),
          icon: Icons.rocket_launch,
          onPressed: _busy ? null : _apply,
          isLoading: _busy,
          isPrimary: true,
        ),
        AxiomButton(
          label: _strings.t('healthCheck'),
          icon: Icons.monitor_heart,
          onPressed: _busy ? null : _checkHealth,
          isPrimary: false,
        ),
      ],
    );
  }

  // --- Logic Implementation ---

  Future<void> _initSourcePath() async {
    final sourcePath = await _sourceService.resolveSourcePath();
    if (!mounted) return;
    setState(() {
      _sourceController.text = sourcePath;
    });
    _log('Source path detected: $sourcePath');
  }

  Future<void> _pickTargetDirectory() async {
    try {
      final dir = await _directoryPicker();
      if (dir == null) {
        _log('[INFO] Directory selection canceled.');
        return;
      }
      if (dir.trim().isEmpty) {
        _log('[WARN] Empty directory path returned.');
        return;
      }
      setState(() {
        _targetController.text = dir;
      });
      _log('Target directory selected: $dir');
    } catch (e) {
      _log('[ERROR] Directory picker failed: $e');
    }
  }

  Future<void> _forceSync() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) {
        return AlertDialog(
          title: Text(_strings.t('forceSync')),
          content: Text(_strings.t('forceSyncConfirm')),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(ctx).pop(false),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () => Navigator.of(ctx).pop(true),
              child: const Text('OK'),
            ),
          ],
        );
      },
    );
    if (confirm != true) return;
    await _syncSource(force: true);
  }

  InstallConfig _config() {
    return InstallConfig(
      sourceRoot: _sourceController.text.trim(),
      targetRoot: _targetController.text.trim(),
      activeProvider: _provider,
      techStackId: _techStackId,
    );
  }

  Future<void> _syncSource({bool force = false}) async {
    setState(() {
      _busy = true;
    });
    _log(_strings.t('logSyncing'));

    final result = await _sourceService.sync(force: force);
    if (!mounted) return;
    setState(() {
      _busy = false;
      _sourceController.text = result.sourcePath;
    });
    _log(result.message);
    if (!result.success) {
      _log('[ERROR] Sync failed.');
    }
  }

  Future<bool> _ensureSourceReady() async {
    final sourceRoot = _sourceController.text.trim();
    if (sourceRoot.isEmpty) {
      _log(
          '[ERROR] Axiom source directory not initialized. Please sync first.');
      return false;
    }

    final requiredDir = Directory('$sourceRoot${Platform.pathSeparator}.agent');
    if (requiredDir.existsSync()) {
      return true;
    }

    _log('[WARN] .agent directory not found. Attempting auto-sync...');
    final result = await _sourceService.sync();
    if (!mounted) return false;
    setState(() {
      _sourceController.text = result.sourcePath;
    });
    _log(result.message);
    return result.success;
  }

  Future<void> _preview() async {
    if (!_validateInput()) return;
    setState(() {
      _busy = true;
    });
    _log('Generating preview plan...');

    try {
      final ready = await _ensureSourceReady();
      if (!ready) return;

      final plan = await _engine.plan(_config());

      _log('--- PREVIEW REPORT ---');
      _log('Total Items: ${plan.items.length}');

      final grouped = <DiffAction, int>{
        DiffAction.create: 0,
        DiffAction.update: 0,
        DiffAction.skip: 0,
      };

      for (final item in plan.items) {
        grouped[item.action] = (grouped[item.action] ?? 0) + 1;
        if (item.action != DiffAction.skip) {
          // Highlight changes
          _log('[${item.action.name.toUpperCase()}] ${item.relativePath}');
        }
      }

      _log(
          'Summary: Create(${grouped[DiffAction.create]}) Update(${grouped[DiffAction.update]}) Skip(${grouped[DiffAction.skip]})');
      _log('----------------------');
    } catch (e) {
      _log('[CRITICAL] Preview failed: $e');
    } finally {
      setState(() {
        _busy = false;
      });
    }
  }

  Future<void> _apply() async {
    if (!_validateInput()) return;
    setState(() {
      _busy = true;
    });
    _log('Starting installation...');

    try {
      final ready = await _ensureSourceReady();
      if (!ready) return;

      final result = await _engine.apply(_config());
      if (result.success) {
        _log('[SUCCESS] Installation verified.');
        _log('Changed files:');
        for (var file in result.applied) {
          _log(' + $file');
        }
      } else {
        _log('[FAILED] Installation failed.');
        _log('Error: ${result.error ?? 'Unknown error'}');
      }
    } catch (e) {
      _log('[CRITICAL] Exception during install: $e');
    } finally {
      setState(() {
        _busy = false;
      });
    }
  }

  Future<void> _checkHealth() async {
    final target = _targetController.text.trim();
    if (target.isEmpty) {
      _log('[ERROR] Target directory required for Health Check.');
      return;
    }

    setState(() {
      _busy = true;
    });
    _log('Running Doctor on: $target');

    try {
      final report = await _doctor.check(target);
      _log('--- DOCTOR REPORT ---');
      _log('Status: ${report.ok ? 'HEALTHY' : 'ISSUES FOUND'}');

      if (report.errors.isNotEmpty) {
        for (var e in report.errors) {
          _log('[ERROR] $e');
        }
      }
      if (report.warnings.isNotEmpty) {
        for (var w in report.warnings) {
          _log('[WARN] $w');
        }
      }
      if (report.ok) {
        _log('No critical issues found.');
      }
      _log('---------------------');
    } catch (e) {
      _log('[CRITICAL] Doctor crashed: $e');
    } finally {
      setState(() {
        _busy = false;
      });
    }
  }

  bool _validateInput() {
    if (_targetController.text.trim().isEmpty) {
      _log('[ERROR] ${_strings.t('logTargetRequired')}');
      return false;
    }
    if (_sourceController.text.trim().isEmpty) {
      _log('[ERROR] ${_strings.t('logSourceRequired')}');
      return false;
    }
    return true;
  }
}
