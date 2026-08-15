import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

class AdaptiveScaffold extends StatelessWidget {
  const AdaptiveScaffold({required this.title, required this.body, super.key});

  final String title;
  final Widget body;

  @override
  Widget build(BuildContext context) {
    if (defaultTargetPlatform == TargetPlatform.iOS) {
      return CupertinoPageScaffold(
        navigationBar: CupertinoNavigationBar(middle: Text(title)),
        // top: true (default): bodies use explicit paddings, so they must not
        // be asked to consume MediaQuery.padding themselves — with top: false
        // the first ~90pt of content hides under the translucent bar.
        child: SafeArea(
          child: Material(color: Colors.transparent, child: body),
        ),
      );
    }
    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: body,
    );
  }
}
