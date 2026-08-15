import '../../l10n/app_localizations.dart';

/// Vietnamese-First Rule: category is a machine code, never a display string.
/// Unknown or missing codes return null so callers drop the category rather
/// than leak a raw server value.
String? categoryLabel(String? code, AppLocalizations l10n) => switch (code) {
  'ELEVATOR' => l10n.categoryElevator,
  'WATER_LEAK' => l10n.categoryWaterLeak,
  'ELECTRICAL_FAULT' => l10n.categoryElectricalFault,
  'HEATING_COOLING' => l10n.categoryHeatingCooling,
  'LIGHTING' => l10n.categoryLighting,
  'DOOR_LOCK' => l10n.categoryDoorLock,
  'APPLIANCE' => l10n.categoryAppliance,
  'STRUCTURAL' => l10n.categoryStructural,
  'CLEANLINESS' => l10n.categoryCleanliness,
  'NOISE' => l10n.categoryNoise,
  'OTHER' => l10n.categoryOther,
  _ => null,
};
