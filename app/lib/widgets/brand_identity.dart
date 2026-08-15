import 'package:flutter/widgets.dart';

class BrandIdentity extends StatelessWidget {
  const BrandIdentity({this.width = 180, super.key});

  final double width;

  @override
  Widget build(BuildContext context) => Center(
    child: Image.asset(
      'assets/brand/lamto-logo.png',
      width: width,
      semanticLabel: 'LÀM TỔ',
    ),
  );
}
