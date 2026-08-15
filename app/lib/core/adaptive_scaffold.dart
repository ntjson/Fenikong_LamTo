import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

class AdaptiveScaffold extends StatelessWidget {
  const AdaptiveScaffold({
    required this.title,
    required this.body,
    this.actions = const [],
    super.key,
  });

  final String title;
  final Widget body;

  /// Bar-level actions: Material app-bar actions, Cupertino navigation-bar
  /// trailing. Keep them few — the Cupertino bar has room for one or two.
  final List<Widget> actions;

  @override
  Widget build(BuildContext context) {
    if (defaultTargetPlatform == TargetPlatform.iOS) {
      return CupertinoPageScaffold(
        navigationBar: CupertinoNavigationBar(
          middle: Text(title),
          trailing: actions.isEmpty
              ? null
              : Row(mainAxisSize: MainAxisSize.min, children: actions),
        ),
        // top: true (default): bodies use explicit paddings, so they must not
        // be asked to consume MediaQuery.padding themselves — with top: false
        // the first ~90pt of content hides under the translucent bar.
        child: SafeArea(
          child: Material(color: Colors.transparent, child: body),
        ),
      );
    }
    return Scaffold(
      appBar: AppBar(title: Text(title), actions: actions),
      body: body,
    );
  }
}
