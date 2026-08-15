import 'package:flutter/widgets.dart';

/// Material "medium" window-class breakpoint: at or above this width the
/// shell uses a navigation rail and content is capped by [PageBody].
const double kExpandedWidthMin = 600;

/// Caps page content at a comfortable reading width on tablets, foldables,
/// and landscape phones; pass-through on compact widths.
class PageBody extends StatelessWidget {
  const PageBody({required this.child, super.key});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 640),
        child: child,
      ),
    );
  }
}
