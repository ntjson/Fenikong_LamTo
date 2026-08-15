import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';

/// DESIGN.md light tokens. Accountability Indigo is primary (≤10% of a screen).
class LamToColors {
  static const primary = Color(0xFF2F3A8F);
  static const onPrimary = Color(0xFFFFFFFF);
  static const bg = Color(0xFFF6F7FB);
  static const surface = Color(0xFFFFFFFF);
  static const ink = Color(0xFF1C2434);
  static const muted = Color(0xFF5B6577);
  static const border = Color(0xFFD7DCE8);
  static const success = Color(0xFF0F7A45);
  static const successBg = Color(0xFFE7F6EE);
  // 5.39:1 on warningBg. The lighter 0xFF9A6700 clears AA by 0.02 and
  // disagreed with the web token; one value, with margin.
  static const warning = Color(0xFF8A5C00);
  static const warningBg = Color(0xFFFFF6DD);
  static const error = Color(0xFFB42318);
  static const errorBg = Color(0xFFFEF3F2);
  static const info = Color(0xFF175CD3);
  static const infoBg = Color(0xFFEFF8FF);
}

/// Complete dark-theme tokens (clarification #6).
class LamToColorsDark {
  // 6.34:1 on Night Ground. The light primary remains a fill color only.
  static const primary = Color(0xFF8A97E8);
  static const bg = Color(0xFF12141C);
  static const surface = Color(0xFF1C2030);
  static const ink = Color(0xFFE8EAF2);
  static const muted = Color(0xFFA0A8B8);
  static const border = Color(0xFF3A4158);
  // Night Ground ink on the light dark-primary (≈6.9:1). White fails AA
  // (2.74:1) on every filled button in dark mode.
  static const onPrimary = Color(0xFF12141C);
  // Semantic tones for Night surfaces: deep tinted chip fills with light ink
  // (the light pastels would glare on Night Ground and fail contrast).
  static const success = Color(0xFF66D19E);
  static const successBg = Color(0xFF163425);
  static const warning = Color(0xFFE2B44C);
  static const warningBg = Color(0xFF362C10);
  static const error = Color(0xFFF2938C);
  static const errorBg = Color(0xFF3B1B18);
  static const info = Color(0xFF7CB5F5);
  static const infoBg = Color(0xFF14273D);
}

/// DESIGN.md semantic roles (Separate States Rule: always paired with a
/// text label, never color alone).
enum StatusTone { success, warning, error, info }

/// Resolves a tone to brightness-correct chip colors.
({Color bg, Color fg}) statusToneColors(BuildContext context, StatusTone tone) {
  final dark = Theme.of(context).brightness == Brightness.dark;
  return switch (tone) {
    StatusTone.success when dark => (
      bg: LamToColorsDark.successBg,
      fg: LamToColorsDark.success,
    ),
    StatusTone.success => (bg: LamToColors.successBg, fg: LamToColors.success),
    StatusTone.warning when dark => (
      bg: LamToColorsDark.warningBg,
      fg: LamToColorsDark.warning,
    ),
    StatusTone.warning => (bg: LamToColors.warningBg, fg: LamToColors.warning),
    StatusTone.error when dark => (
      bg: LamToColorsDark.errorBg,
      fg: LamToColorsDark.error,
    ),
    StatusTone.error => (bg: LamToColors.errorBg, fg: LamToColors.error),
    StatusTone.info when dark => (
      bg: LamToColorsDark.infoBg,
      fg: LamToColorsDark.info,
    ),
    StatusTone.info => (bg: LamToColors.infoBg, fg: LamToColors.info),
  };
}

/// DESIGN.md status-chip: pill, semantic bg + ink, label (+ optional icon).
/// The one chip vocabulary for report status and evidence state.
class StatusChip extends StatelessWidget {
  const StatusChip({
    required this.tone,
    required this.label,
    this.icon,
    super.key,
  });

  final StatusTone tone;
  final String label;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    final colors = statusToneColors(context, tone);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: colors.bg,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 16, color: colors.fg),
            const SizedBox(width: 6),
          ],
          Flexible(
            child: Text(
              label,
              style: Theme.of(context).textTheme.labelMedium?.copyWith(
                color: colors.fg,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// Inline outcome notice: tinted semantic container + icon + text. This is
/// the app's snack-bar replacement — snack bars need a Material Scaffold host
/// that the iOS Cupertino tab shell does not provide, so outcomes render
/// inline where the user is looking. Live-region so screen readers announce
/// the state change (Separate States Rule: tone + icon + text, never color
/// alone).
class StatusNotice extends StatelessWidget {
  const StatusNotice({
    required this.tone,
    required this.message,
    this.icon,
    super.key,
  });

  final StatusTone tone;
  final String message;
  final IconData? icon;

  static IconData _defaultIcon(StatusTone tone) => switch (tone) {
    StatusTone.success => Icons.check_circle_outline,
    StatusTone.error => Icons.error_outline,
    StatusTone.warning || StatusTone.info => Icons.info_outline,
  };

  @override
  Widget build(BuildContext context) {
    final colors = statusToneColors(context, tone);
    return Semantics(
      liveRegion: true,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: colors.bg,
          borderRadius: BorderRadius.circular(10),
        ),
        child: Row(
          children: [
            Icon(icon ?? _defaultIcon(tone), color: colors.fg),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                message,
                style: Theme.of(
                  context,
                ).textTheme.bodyMedium?.copyWith(color: colors.fg),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Tabular-figure body style for amounts inside list rows. Full Record Ink on
/// purpose: financial figures are primary copy (DESIGN.md), not muted metadata.
TextStyle? listAmountStyle(BuildContext context) => Theme.of(context)
    .textTheme
    .bodyMedium
    ?.copyWith(fontFeatures: const [FontFeature.tabularFigures()]);

/// Money / VND text style with real tabular figures (DESIGN.md).
TextStyle moneyTextStyle(TextTheme base, {Color? color}) {
  return (base.titleMedium ?? const TextStyle()).copyWith(
    fontFeatures: const [FontFeature.tabularFigures()],
    color: color,
    fontWeight: FontWeight.w600,
  );
}

ThemeData lamToTheme(Brightness brightness) {
  final isDark = brightness == Brightness.dark;
  final surface = isDark ? LamToColorsDark.surface : LamToColors.surface;
  final bg = isDark ? LamToColorsDark.bg : LamToColors.bg;
  final onSurface = isDark ? LamToColorsDark.ink : LamToColors.ink;
  final outline = isDark ? LamToColorsDark.border : LamToColors.border;
  final scheme = ColorScheme.fromSeed(
    seedColor: LamToColors.primary,
    brightness: brightness,
    primary: isDark ? LamToColorsDark.primary : LamToColors.primary,
    onPrimary: isDark ? LamToColorsDark.onPrimary : LamToColors.onPrimary,
    // Dark keeps the derived light-tone error: #B42318 on Night Ground is
    // ~2.8:1, below the WCAG AA baseline for error text.
    error: isDark ? null : LamToColors.error,
    surface: surface,
    onSurface: onSurface,
    outline: outline,
  );
  final baseText = Typography.material2021(
    platform: defaultTargetPlatform,
  ).black.apply(bodyColor: onSurface, displayColor: onSurface);
  final textTheme = baseText.copyWith(
    titleMedium: moneyTextStyle(baseText, color: onSurface),
  );
  return ThemeData(
    useMaterial3: true,
    brightness: brightness,
    colorScheme: scheme,
    scaffoldBackgroundColor: bg,
    textTheme: textTheme,
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(48)),
    ),
    inputDecorationTheme: InputDecorationTheme(
      border: const OutlineInputBorder(),
      filled: true,
      fillColor: surface,
    ),
  );
}
