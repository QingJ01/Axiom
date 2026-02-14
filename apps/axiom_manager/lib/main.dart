import 'package:axiom_manager/core/doctor/doctor_service.dart';
import 'package:axiom_manager/core/installer/install_engine.dart';
import 'package:axiom_manager/core/installer/install_models.dart';
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
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1C6E8C)),
        useMaterial3: true,
      ),
      home: const InstallerHomePage(),
    );
  }
}

class InstallerHomePage extends StatefulWidget {
  const InstallerHomePage({super.key});

  @override
  State<InstallerHomePage> createState() => _InstallerHomePageState();
}

class _InstallerHomePageState extends State<InstallerHomePage> {
  static const providers = <String>[
    'gemini_cli',
    'claude_code',
    'codex',
    'opencode',
    'gemini',
    'claude',
    'copilot',
  ];

  final _sourceController = TextEditingController();
  final _targetController = TextEditingController();
  final _engine = InstallEngine();
  final _doctor = DoctorService();

  String _provider = 'gemini_cli';
  bool _busy = false;
  String _output = '就绪';

  @override
  void dispose() {
    _sourceController.dispose();
    _targetController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Axiom Manager')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            TextField(
              controller: _sourceController,
              decoration: const InputDecoration(
                labelText: 'Axiom 源目录',
                hintText: '例如: C:/repo/axiom',
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _targetController,
              decoration: const InputDecoration(
                labelText: '目标项目目录',
                hintText: '例如: D:/work/my_project',
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                const Text('Provider: '),
                const SizedBox(width: 8),
                DropdownButton<String>(
                  value: _provider,
                  items:
                      providers
                          .map(
                            (p) => DropdownMenuItem<String>(
                              value: p,
                              child: Text(p),
                            ),
                          )
                          .toList(),
                  onChanged:
                      _busy
                          ? null
                          : (value) {
                            if (value == null) return;
                            setState(() {
                              _provider = value;
                            });
                          },
                ),
              ],
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                FilledButton(
                  onPressed: _busy ? null : _preview,
                  child: const Text('预览变更'),
                ),
                FilledButton(
                  onPressed: _busy ? null : _apply,
                  child: const Text('执行导入'),
                ),
                OutlinedButton(
                  onPressed: _busy ? null : _checkHealth,
                  child: const Text('健康检查'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Expanded(
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  border: Border.all(
                    color: Theme.of(context).colorScheme.outlineVariant,
                  ),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: SingleChildScrollView(child: Text(_output)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  InstallConfig _config() {
    return InstallConfig(
      sourceRoot: _sourceController.text.trim(),
      targetRoot: _targetController.text.trim(),
      activeProvider: _provider,
    );
  }

  Future<void> _preview() async {
    if (!_validateInput()) return;
    setState(() {
      _busy = true;
      _output = '正在预览...';
    });

    try {
      final plan = await _engine.plan(_config());
      final grouped = <DiffAction, int>{
        DiffAction.create: 0,
        DiffAction.update: 0,
        DiffAction.skip: 0,
      };
      for (final item in plan.items) {
        grouped[item.action] = (grouped[item.action] ?? 0) + 1;
      }

      final lines = <String>[
        '预览完成',
        'create: ${grouped[DiffAction.create]}',
        'update: ${grouped[DiffAction.update]}',
        'skip: ${grouped[DiffAction.skip]}',
        '',
      ];
      for (final item in plan.items.take(40)) {
        lines.add('${item.action.name.padRight(6)} ${item.relativePath}');
      }
      setState(() {
        _output = lines.join('\n');
      });
    } catch (e) {
      setState(() {
        _output = '预览失败: $e';
      });
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
      _output = '正在执行导入...';
    });

    try {
      final result = await _engine.apply(_config());
      if (result.success) {
        setState(() {
          _output = '导入成功\n变更文件数: ${result.applied.length}';
        });
      } else {
        setState(() {
          _output = '导入失败\n${result.error ?? '未知错误'}';
        });
      }
    } catch (e) {
      setState(() {
        _output = '导入异常: $e';
      });
    } finally {
      setState(() {
        _busy = false;
      });
    }
  }

  Future<void> _checkHealth() async {
    final target = _targetController.text.trim();
    if (target.isEmpty) {
      setState(() {
        _output = '请先填写目标项目目录';
      });
      return;
    }

    setState(() {
      _busy = true;
      _output = '正在健康检查...';
    });

    try {
      final report = await _doctor.check(target);
      final lines = <String>['健康检查结果: ${report.ok ? 'OK' : 'FAILED'}'];
      if (report.errors.isNotEmpty) {
        lines.add('Errors:');
        lines.addAll(report.errors.map((e) => '- $e'));
      }
      if (report.warnings.isNotEmpty) {
        lines.add('Warnings:');
        lines.addAll(report.warnings.map((w) => '- $w'));
      }
      setState(() {
        _output = lines.join('\n');
      });
    } catch (e) {
      setState(() {
        _output = '健康检查异常: $e';
      });
    } finally {
      setState(() {
        _busy = false;
      });
    }
  }

  bool _validateInput() {
    if (_sourceController.text.trim().isEmpty ||
        _targetController.text.trim().isEmpty) {
      setState(() {
        _output = '请先填写 Axiom 源目录和目标项目目录';
      });
      return false;
    }
    return true;
  }
}
