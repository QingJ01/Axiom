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
            backgroundColor: colorScheme.primary, // This is Accent (Sky 400)
            foregroundColor: const Color(0xFF0F172A), // Dark text on bright button
            elevation: 4,
            shadowColor: colorScheme.primary.withValues(alpha: 0.4),
          )
        : OutlinedButton.styleFrom(
            foregroundColor: colorScheme.primary,
            side: BorderSide(color: colorScheme.primary.withValues(alpha: 0.5)),
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
