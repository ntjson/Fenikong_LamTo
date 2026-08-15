import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:lamto_api/lamto_api.dart';

import '../../core/error_retry.dart';
import '../../core/format.dart';
import '../../l10n/app_localizations.dart';
import '../../theme.dart';
import 'transparency_repository.dart';

/// Fund balance history. Home uses the compact line; Ledger uses the full view.
class FundChart extends ConsumerWidget {
  const FundChart({
    super.key,
    required this.range,
    this.compact = false,
    this.onTap,
  });

  final String range;
  final bool compact;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    return switch (ref.watch(fundSeriesProvider(range))) {
      AsyncData(:final value) => Semantics(
        label: _semanticsLabel(context, l10n, value),
        button: onTap != null,
        child: ExcludeSemantics(child: _chart(context, l10n, value)),
      ),
      AsyncError(:final error) => ErrorRetry(
        error: error,
        onRetry: () => ref.invalidate(fundSeriesProvider(range)),
      ),
      _ => const SizedBox(
        height: 160,
        child: Center(child: CircularProgressIndicator.adaptive()),
      ),
    };
  }

  String _semanticsLabel(
    BuildContext context,
    AppLocalizations l10n,
    FundSeries series,
  ) {
    final locale = Localizations.localeOf(context).toLanguageTag();
    final date = DateFormat(range == '30d' ? 'd/M' : 'M/yyyy', locale);
    final values = series.points.map(
      (point) =>
          '${date.format(point.periodStart)}: '
          '${l10n.fundChartBalanceValue(formatVnd(point.balanceVnd))}, '
          '${l10n.fundChartInflowValue(formatVnd(point.inflowsVnd))}, '
          '${l10n.fundChartOutflowValue(formatVnd(point.outflowsVnd))}',
    );
    return '${l10n.fundChartSemantics}. ${values.join('. ')}';
  }

  Widget _chart(
    BuildContext context,
    AppLocalizations l10n,
    FundSeries series,
  ) {
    final points = series.points.toList();
    if (points.isEmpty) return const SizedBox.shrink();
    final line = _balanceLine(context, points);
    if (compact) {
      return InkWell(
        onTap: onTap,
        child: SizedBox(height: 140, child: line),
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(height: 180, child: line),
        const SizedBox(height: 16),
        Text(
          l10n.fundChartFlowsTitle,
          style: Theme.of(context).textTheme.titleSmall,
        ),
        const SizedBox(height: 8),
        SizedBox(height: 120, child: _flowsBars(context, points)),
        const SizedBox(height: 8),
        // Names each series; color never carries the meaning alone.
        Wrap(
          spacing: 16,
          runSpacing: 4,
          children: [
            _legendItem(
              context,
              _inflowColor(context),
              l10n.fundChartInflowLabel,
            ),
            _legendItem(
              context,
              _outflowColor(context),
              l10n.fundChartOutflowLabel,
            ),
          ],
        ),
      ],
    );
  }

  // Tabular Column Rule: money-flow series use the brand/info pair — never
  // success/error, which are reserved for evidence state.
  Color _inflowColor(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark
      ? LamToColorsDark.primary
      : LamToColors.primary;

  Color _outflowColor(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark
      ? LamToColorsDark.info
      : LamToColors.info;

  Widget _legendItem(BuildContext context, Color color, String label) => Row(
    mainAxisSize: MainAxisSize.min,
    children: [
      Container(
        width: 12,
        height: 12,
        decoration: BoxDecoration(
          color: color,
          borderRadius: BorderRadius.circular(3),
        ),
      ),
      const SizedBox(width: 6),
      Text(label, style: Theme.of(context).textTheme.labelSmall),
    ],
  );

  Duration _animationDuration(BuildContext context) =>
      MediaQuery.disableAnimationsOf(context)
      ? Duration.zero
      : const Duration(milliseconds: 200);

  Widget _balanceLine(BuildContext context, List<FundSeriesPoint> points) {
    final scheme = Theme.of(context).colorScheme;
    return LineChart(
      LineChartData(
        gridData: const FlGridData(show: false),
        borderData: FlBorderData(show: false),
        titlesData: FlTitlesData(
          leftTitles: const AxisTitles(),
          topTitles: const AxisTitles(),
          rightTitles: const AxisTitles(),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: !compact,
              interval: (points.length / 6).ceilToDouble(),
              getTitlesWidget: (value, _) =>
                  _periodLabel(context, points, value),
            ),
          ),
        ),
        lineTouchData: LineTouchData(enabled: !compact),
        lineBarsData: [
          LineChartBarData(
            spots: [
              for (var i = 0; i < points.length; i++)
                FlSpot(i.toDouble(), points[i].balanceVnd.toDouble()),
            ],
            isCurved: false,
            color: scheme.primary,
            dotData: const FlDotData(show: false),
            belowBarData: BarAreaData(
              show: true,
              color: scheme.primary.withValues(alpha: 0.12),
            ),
          ),
        ],
      ),
      duration: _animationDuration(context),
    );
  }

  Widget _flowsBars(BuildContext context, List<FundSeriesPoint> points) {
    final inflow = _inflowColor(context);
    final outflow = _outflowColor(context);
    return BarChart(
      BarChartData(
        gridData: const FlGridData(show: false),
        borderData: FlBorderData(show: false),
        titlesData: const FlTitlesData(
          leftTitles: AxisTitles(),
          topTitles: AxisTitles(),
          rightTitles: AxisTitles(),
          bottomTitles: AxisTitles(),
        ),
        barGroups: [
          for (var i = 0; i < points.length; i++)
            BarChartGroupData(
              x: i,
              barRods: [
                BarChartRodData(
                  toY: points[i].inflowsVnd.toDouble(),
                  color: inflow,
                  width: 6,
                ),
                BarChartRodData(
                  toY: points[i].outflowsVnd.toDouble(),
                  color: outflow,
                  width: 6,
                ),
              ],
            ),
        ],
      ),
      duration: _animationDuration(context),
    );
  }

  Widget _periodLabel(
    BuildContext context,
    List<FundSeriesPoint> points,
    double value,
  ) {
    final i = value.toInt();
    if (i < 0 || i >= points.length) return const SizedBox.shrink();
    final pattern = range == '30d' ? 'd/M' : 'M/yy';
    final label = DateFormat(
      pattern,
      Localizations.localeOf(context).toLanguageTag(),
    ).format(points[i].periodStart);
    return Padding(
      padding: const EdgeInsets.only(top: 4),
      child: Text(label, style: Theme.of(context).textTheme.labelSmall),
    );
  }
}
