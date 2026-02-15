import 'package:flutter/material.dart';

class AxiomButton extends StatelessWidget {
  const AxiomButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.icon,
    this.isPrimary = true,
    this.isLoading = false,
  });

  final String label;
  final VoidCallback? onPressed;
  final IconData? icon;
  final bool isPrimary;
  final bool isLoading;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    final style = isPrimary
        ? ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF2563EB),
            foregroundColor: Colors.white,
            elevation: 0,
          )
        : OutlinedButton.styleFrom(
            foregroundColor: colorScheme.onSurface,
            side: const BorderSide(color: Color(0xFF2B395A)),
          );

    return SizedBox(
      height: 48,
      child: isPrimary
          ? ElevatedButton(
              onPressed: isLoading ? null : onPressed,
              style: style,
              child: _buildContent(),
            )
          : OutlinedButton(
              onPressed: isLoading ? null : onPressed,
              style: style,
              child: _buildContent(),
            ),
    );
  }

  Widget _buildContent() {
    if (isLoading) {
      return const SizedBox(
        width: 20,
        height: 20,
        child: CircularProgressIndicator(
          strokeWidth: 2,
          color: Colors.white, // Or adapt based on background
        ),
      );
    }
    if (icon != null) {
      return Row(
        mainAxisSize: MainAxisSize.max,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 20),
          const SizedBox(width: 6),
          Flexible(
            child: Text(
              label,
              overflow: TextOverflow.ellipsis,
              maxLines: 1,
              softWrap: false,
            ),
          ),
        ],
      );
    }
    return Text(label);
  }
}
