/// Returns the reference from `lamto-bill:<reference>`, or null otherwise.
String? billReferenceFromQr(String raw) {
  const prefix = 'lamto-bill:';
  if (!raw.startsWith(prefix)) return null;
  final reference = raw.substring(prefix.length);
  return reference.isEmpty ? null : reference;
}
