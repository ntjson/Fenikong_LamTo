import 'package:intl/intl.dart';

/// Integer VND with Vietnamese grouping (DESIGN.md: tabular numerals come
/// from the Amount text style; this handles digits + currency sign).
final _vnd = NumberFormat.decimalPattern('vi');

String formatVnd(int amount) => '${_vnd.format(amount)} ₫';

/// Standalone month label from locale date symbols ("Tháng 1" … "Tháng 12"
/// in Vietnamese). [month] is 1-based.
String formatMonthLabel(int month, String locale) =>
    DateFormat.LLLL(locale).format(DateTime(2000, month));
