/// Allowlisted deep-link map (spec 7.4): report, ledger entry, bill, or feed.
///
/// Anything unknown falls back to the feed — a link can never widen access.
/// [event_key] / push destinations carry **only allowlisted type+id** (A8);
/// the parser does not treat keys as authorization. Every destination
/// re-fetches through the authenticated API and its own failure state is the
/// safe landing for a 403/404.
///
/// **A2 Case deep-link fallback:** there is no resident Case detail screen.
/// Deep links of type/entity `case` (and `correction` / `work` / unknown)
/// safely fall back to [DeepLinkFeed]. Examples:
/// - `parseEventKey('triage.status:case:3')` → [DeepLinkFeed]
/// - `parsePushLink(type: 'case', id: '3')` → [DeepLinkFeed]
sealed class DeepLink {
  const DeepLink();
}

class DeepLinkReport extends DeepLink {
  const DeepLinkReport(this.id);
  final int id;
  @override
  bool operator ==(Object other) => other is DeepLinkReport && other.id == id;
  @override
  int get hashCode => Object.hash('report', id);
}

class DeepLinkLedger extends DeepLink {
  const DeepLinkLedger(this.id);
  final int id;
  @override
  bool operator ==(Object other) => other is DeepLinkLedger && other.id == id;
  @override
  int get hashCode => Object.hash('ledger', id);
}

class DeepLinkBill extends DeepLink {
  const DeepLinkBill(this.id);
  final int id;
  @override
  bool operator ==(Object other) => other is DeepLinkBill && other.id == id;
  @override
  int get hashCode => Object.hash('bill', id);
}

class DeepLinkFeed extends DeepLink {
  const DeepLinkFeed();
  @override
  bool operator ==(Object other) => other is DeepLinkFeed;
  @override
  int get hashCode => 'feed'.hashCode;
}

/// Push payload data: `{'type': report|case|ledger|bill|notifications, 'id': ...}`.
///
/// Allowlist only: `report`, `ledger`, or `bill` plus a numeric id.
/// `case`, `notifications`, missing/invalid
/// ids, and any other type → [DeepLinkFeed] (A2). Not an authorization check
/// (A8) — the destination screen re-fetches via the authenticated API.
DeepLink parsePushLink({String? type, String? id}) {
  final parsed = int.tryParse(id ?? '');
  return switch (type) {
    'report' when parsed != null => DeepLinkReport(parsed),
    'ledger' when parsed != null => DeepLinkLedger(parsed),
    'bill' when parsed != null => DeepLinkBill(parsed),
    _ => const DeepLinkFeed(),
  };
}

/// Feed `event_key`: `'{code}:{entity}:{id}[:{suffix}]'`.
///
/// Allowlist only: entity `report`, `entry`, or `bill`. Entity `case`,
/// `correction`, `work`, unknown, or
/// non-numeric id → [DeepLinkFeed] (A2). Keys are not treated as authorization
/// (A8) — destinations re-fetch through the authenticated API.
DeepLink parseEventKey(String eventKey) {
  final parts = eventKey.split(':');
  if (parts.length < 3) return const DeepLinkFeed();
  final id = int.tryParse(parts[2]);
  if (id == null) return const DeepLinkFeed();
  return switch (parts[1]) {
    'report' => DeepLinkReport(id),
    'entry' => DeepLinkLedger(id),
    'bill' => DeepLinkBill(id),
    _ => const DeepLinkFeed(),
  };
}
