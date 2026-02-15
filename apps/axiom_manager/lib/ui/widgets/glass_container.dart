import 'package:flutter/material.dart';

class GlassContainer extends StatelessWidget {
  const GlassContainer({
    super.key,
    required this.child,
    this.opacity = 0.1,
    this.blur = 10,
    this.borderRadius = 16,
    this.borderColor,
  });

  final Widget child;
  final double opacity;
  final double blur;
  final double borderRadius;
  final Color? borderColor;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(borderRadius),
        border: Border.all(
          color: borderColor ?? const Color(0xFF1F2A44),
          width: 1,
        ),
      ),
      child: child,
    );
  }
}
