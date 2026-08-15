import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/failure.dart';
import '../../core/adaptive_buttons.dart';
import '../../core/adaptive_scaffold.dart';
import '../../core/adaptive_page_route.dart';
import '../../core/page_body.dart';
import '../../l10n/app_localizations.dart';
import '../../widgets/brand_identity.dart';
import '../settings/api_base_url_tile.dart';
import 'registration_screen.dart';
import 'session_controller.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key, this.initialIdentifier = ''});

  final String initialIdentifier;
  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  late final TextEditingController _id;
  final _pw = TextEditingController();
  String? _error;
  bool _busy = false;
  bool _obscure = true;

  @override
  void initState() {
    super.initState();
    _id = TextEditingController(text: widget.initialIdentifier);
  }

  @override
  void dispose() {
    _id.dispose();
    _pw.dispose();
    super.dispose();
  }

  Future<void> _submit(AppLocalizations l10n) async {
    final id = _id.text.trim();
    final pw = _pw.text;
    if (id.isEmpty || pw.isEmpty) {
      // No server round-trip for a knowable outcome; errGeneric would hide
      // what to fix.
      setState(() => _error = l10n.loginMissingFields);
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await ref.read(sessionControllerProvider.notifier).signIn(id, pw);
      // Let the platform password manager offer to save the credentials.
      TextInput.finishAutofillContext();
    } on DioException catch (e) {
      if (mounted) {
        setState(() => _error = failureMessage(Failure.fromDio(e), l10n));
      }
    } catch (_) {
      if (mounted) setState(() => _error = l10n.errGeneric);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return AdaptiveScaffold(
      title: l10n.loginTitle,
      body: PageBody(
        child: AutofillGroup(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: ListView(
              children: [
                const BrandIdentity(width: 200),
                const SizedBox(height: 20),
                TextField(
                  controller: _id,
                  decoration: InputDecoration(labelText: l10n.loginIdentifier),
                  keyboardType: TextInputType.emailAddress,
                  textInputAction: TextInputAction.next,
                  autofillHints: const [AutofillHints.username],
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _pw,
                  obscureText: _obscure,
                  decoration: InputDecoration(
                    labelText: l10n.loginPassword,
                    suffixIcon: IconButton(
                      tooltip: _obscure
                          ? l10n.loginShowPassword
                          : l10n.loginHidePassword,
                      icon: Icon(
                        _obscure
                            ? Icons.visibility_outlined
                            : Icons.visibility_off_outlined,
                      ),
                      onPressed: () => setState(() => _obscure = !_obscure),
                    ),
                  ),
                  textInputAction: TextInputAction.done,
                  autofillHints: const [AutofillHints.password],
                  onSubmitted: (_) => _busy ? null : _submit(l10n),
                ),
                if (_error != null) ...[
                  const SizedBox(height: 12),
                  Text(
                    _error!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                ],
                const SizedBox(height: 20),
                AdaptiveFilledButton(
                  onPressed: _busy ? null : () => _submit(l10n),
                  child: Text(l10n.loginSubmit),
                ),
                AdaptiveTextButton(
                  onPressed: _busy
                      ? null
                      : () => Navigator.of(context).push(
                          adaptivePageRoute<void>(
                            builder: (_) => const RegistrationScreen(),
                          ),
                        ),
                  child: Text(l10n.registrationOpen),
                ),
                // Not debug-gated: a released APK must be retargetable at a
                // fresh quick-tunnel URL without a rebuild.
                const SizedBox(height: 24),
                const ApiBaseUrlTile(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
