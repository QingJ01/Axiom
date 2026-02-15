import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

class AppLogo extends StatelessWidget {
  const AppLogo({
    super.key,
    this.size = 28,
  });

  final double size;

  @override
  Widget build(BuildContext context) {
    return SvgPicture.asset(
      'logo.svg',
      width: size,
      height: size,
      fit: BoxFit.contain,
    );
  }
}
