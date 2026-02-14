import 'dart:io';

import 'package:axiom_manager/core/doctor/doctor_service.dart';
import 'package:axiom_manager/core/installer/install_engine.dart';
import 'package:axiom_manager/core/installer/install_models.dart';
import 'package:axiom_manager/core/source/axiom_source_service.dart';
import 'package:axiom_manager/ui/theme.dart';
import 'package:axiom_manager/ui/widgets/axiom_button.dart';
import 'package:axiom_manager/ui/widgets/glass_container.dart';
import 'package:axiom_manager/ui/widgets/terminal_output.dart';
import 'package:file_selector/file_selector.dart';
import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Axiom Manager',
      debugShowCheckedModeBanner: false,
      theme: AxiomTheme.darkTheme,
      home: const InstallerHomePage(),
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
    this.engine,
    this.doctor,
    this.sourceService,
    this.directoryPicker,
  });

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
  bool _showLegacyProviders = false;
  bool _busy = false;
  String _output = '> Axiom Manager Ready.\n> Waiting for user input...';

  @override
  void initState() {
    super.initState();
    _engine = widget.engine ?? InstallEngine();
    _doctor = widget.doctor ?? DoctorService();
    _sourceService = widget.sourceService ?? AxiomSourceService();
    _directoryPicker = widget.directoryPicker ?? (() => getDirectoryPath());
    _initSourcePath();
  }

  @override
  void dispose() {
    _sourceController.dispose();
    _targetController.dispose();
    _scrollController.dispose();
    super.dispose();
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

  @override
  Widget build(BuildContext context) {
    final providerOptions = _allProviders
        .where((p) => _showLegacyProviders || !p.legacy)
        .toList();

    return Scaffold(
      body: Stack(
        children: [
          // Background Elements could go here (e.g. stars, gradient mesh)
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                gradient: RadialGradient(
                  center: const Alignment(0.8, -0.5),
                  radius: 1.2,
                  colors: [
                    AxiomTheme.accent.withValues(alpha: 0.15),
                    AxiomTheme.primary,
                  ],
                ),
              ),
            ),
          ),
          
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                children: [
                   _buildHeader(),
                   const SizedBox(height: 24),
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
                                   icon: const Icon(Icons.cleaning_services, size: 16),
                                   label: const Text('Clear Console'),
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
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        Icon(Icons.token, size: 32, color: AxiomTheme.accent),
        const SizedBox(width: 12),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'AXIOM MANAGER',
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
            labelText: 'Axiom Source Path',
            prefixIcon: const Icon(Icons.folder_shared_outlined),
            suffixIcon: IconButton(
              icon: const Icon(Icons.sync),
              tooltip: 'Sync Source',
              onPressed: _busy ? null : _syncSource,
            ),
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
            decoration: const InputDecoration(
              labelText: 'Target Directory',
              prefixIcon: Icon(Icons.folder_open_outlined),
            ),
          ),
        ),
        const SizedBox(width: 12),
        IconButton.filledTonal(
          onPressed: _busy ? null : _pickTargetDirectory,
          icon: const Icon(Icons.more_horiz),
          tooltip: 'Browse...',
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
          decoration: const InputDecoration(
            prefixIcon: Icon(Icons.psychology),
            labelText: 'Active Provider',
          ),
          dropdownColor: AxiomTheme.surface,
          items: options.map((p) {
            return DropdownMenuItem<String>(
              value: p.id,
              child: Text(p.id),
            );
          }).toList(),
          onChanged: _busy ? null : (value) {
            if (value == null) return;
            setState(() {
              _provider = value;
              final selected = _allProviders.firstWhere((p) => p.id == value);
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
          onChanged: _busy ? null : (value) {
            setState(() {
              _showLegacyProviders = value ?? false;
              if (!_showLegacyProviders && (_provider == 'gemini' || _provider == 'claude')) {
                _provider = _provider == 'gemini' ? 'gemini_cli' : 'claude_code';
                _log('[WARN] Legacy provider hidden. Auto-switched to $_provider');
              }
            });
          },
          title: const Text('Show Legacy Providers'),
          controlAffinity: ListTileControlAffinity.leading,
          dense: true,
          contentPadding: EdgeInsets.zero,
        ),
      ],
    );
  }

  Widget _buildActionButtons() {
    return Wrap(
      spacing: 12,
      runSpacing: 12,
      children: [
        AxiomButton(
          label: 'Preview Changes',
          icon: Icons.preview,
          onPressed: _busy ? null : _preview,
          isPrimary: false,
        ),
        AxiomButton(
          label: 'Inject / Apply',
          icon: Icons.rocket_launch,
          onPressed: _busy ? null : _apply,
          isLoading: _busy,
          isPrimary: true,
        ),
        AxiomButton(
          label: 'Health Check',
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
    final dir = await _directoryPicker();
    if (dir == null || dir.trim().isEmpty) return;
    setState(() {
      _targetController.text = dir;
    });
    _log('Target directory selected: $dir');
  }

  InstallConfig _config() {
    return InstallConfig(
      sourceRoot: _sourceController.text.trim(),
      targetRoot: _targetController.text.trim(),
      activeProvider: _provider,
    );
  }

  Future<void> _syncSource() async {
    setState(() {
      _busy = true;
    });
    _log('Syncing Axiom source...');

    final result = await _sourceService.sync();
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
      _log('[ERROR] Axiom source directory not initialized. Please sync first.');
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
      
      _log('Summary: Create(${grouped[DiffAction.create]}) Update(${grouped[DiffAction.update]}) Skip(${grouped[DiffAction.skip]})');
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
        for (var e in report.errors) _log('[ERROR] $e');
      }
      if (report.warnings.isNotEmpty) {
        for (var w in report.warnings) _log('[WARN] $w');
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
      _log('[ERROR] Target project directory is empty.');
      return false;
    }
    if (_sourceController.text.trim().isEmpty) {
      _log('[ERROR] Axiom Source Path is empty. Please sync.');
      return false;
    }
    return true;
  }
}
