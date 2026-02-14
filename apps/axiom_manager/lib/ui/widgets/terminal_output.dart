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
        color: Colors.black.withValues(alpha: 0.8),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.5),
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
                'TERMINAL OUTPUT',
                style: TextStyle(
                  fontFamily: 'Consolas',
                  fontSize: 12,
                  color: Colors.grey,
                  letterSpacing: 1.5,
                ),
              ),
              IconButton(
                icon: const Icon(Icons.copy, size: 16, color: Colors.grey),
                onPressed: () {
                  Clipboard.setData(ClipboardData(text: output));
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Copied to clipboard'),
                      duration: Duration(seconds: 1),
                    ),
                  );
                },
                tooltip: 'Copy Output',
              ),
            ],
          ),
          const Divider(color: Colors.grey, height: 20, thickness: 0.5),
          Expanded(
            child: SingleChildScrollView(
              controller: scrollController,
              child: SelectableText(
                output,
                style: const TextStyle(
                  fontFamily: 'Consolas',
                  color: Color(0xFF22C55E), // Terminal Green
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
