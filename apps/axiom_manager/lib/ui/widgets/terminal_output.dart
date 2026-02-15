import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class TerminalOutput extends StatelessWidget {
  const TerminalOutput({
    super.key,
    required this.output,
    this.scrollController,
  });

  final String output;
  final ScrollController? scrollController;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF0C1322),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: const Color(0xFF1F2A44),
        ),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'LOG OUTPUT',
                style: TextStyle(
                  fontFamily: 'Consolas',
                  fontSize: 12,
                  color: Color(0xFF9CA3AF),
                  letterSpacing: 1.2,
                ),
              ),
              IconButton(
                icon:
                    const Icon(Icons.copy, size: 16, color: Color(0xFF9CA3AF)),
                onPressed: () {
                  Clipboard.setData(ClipboardData(text: output));
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Copied'),
                      duration: Duration(seconds: 1),
                    ),
                  );
                },
                tooltip: 'Copy Output',
              ),
            ],
          ),
          const Divider(color: Color(0xFF24334F), height: 20, thickness: 0.8),
          Expanded(
            child: SingleChildScrollView(
              controller: scrollController,
              child: SelectableText(
                output,
                style: const TextStyle(
                  fontFamily: 'Consolas',
                  color: Color(0xFFE5E7EB),
                  fontSize: 13,
                  height: 1.4,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
