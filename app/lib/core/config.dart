/// Compile-time default only. Prefer [apiBaseUrlProvider] at runtime so the
/// user can point a installed APK at a new Cloudflare tunnel without rebuild.
const String apiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://10.0.2.2:8000',
);
