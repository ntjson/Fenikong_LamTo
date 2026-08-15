import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../../core/adaptive_buttons.dart';
import '../../core/adaptive_scaffold.dart';
import '../../core/error_retry.dart';
import '../../core/page_body.dart';
import '../../l10n/app_localizations.dart';
import 'gate_repository.dart';
import 'plate_text.dart';

class GateRegistrationScreen extends StatefulWidget {
  const GateRegistrationScreen({
    super.key,
    required this.repository,
    this.picker,
  });
  final GateRepository repository;
  final ImagePicker? picker;
  @override
  State<GateRegistrationScreen> createState() => _GateRegistrationScreenState();
}

class _GateRegistrationScreenState extends State<GateRegistrationScreen> {
  final plate = TextEditingController();
  Map<String, dynamic>? data;
  Object? error;
  bool busy = false;
  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    plate.dispose();
    super.dispose();
  }

  Future<void> _run(Future<void> Function() action) async {
    setState(() {
      busy = true;
      error = null;
    });
    try {
      await action();
      await _load();
    } catch (e) {
      if (mounted) setState(() => error = e);
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  Future<void> _load() async {
    try {
      final value = await widget.repository.registrations();
      if (mounted) setState(() => data = value);
    } catch (e) {
      if (mounted) setState(() => error = e);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final plates = (data?['plates'] as List?) ?? const [];
    final face = data?['face'] as Map?;
    return AdaptiveScaffold(
      title: l10n.gateRegistrationTitle,
      body: PageBody(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: ListView(
            children: [
              if (error != null) ...[
                ErrorRetry(error: error!, onRetry: _load),
                const SizedBox(height: 16),
              ] else if (data == null) ...[
                const Center(child: CircularProgressIndicator.adaptive()),
                const SizedBox(height: 16),
              ],
              TextField(
                controller: plate,
                decoration: InputDecoration(
                  labelText: l10n.gatePlateLabel,
                  helperText: normalizePlateText(plate.text),
                ),
                onChanged: (_) => setState(() {}),
              ),
              const SizedBox(height: 12),
              AdaptiveFilledButton(
                onPressed:
                    busy || !isPlausiblePlate(normalizePlateText(plate.text))
                    ? null
                    : () => _run(() => widget.repository.addPlate(plate.text)),
                child: Text(l10n.gateSubmitPlate),
              ),
              const SizedBox(height: 8),
              for (final item in plates.cast<Map>())
                ListTile(
                  title: Text('${item['plate']}'),
                  subtitle: Text(
                    _statusText(
                      l10n,
                      '${item['status']}',
                      '${item['review_note'] ?? ''}',
                    ),
                  ),
                  trailing: IconButton(
                    tooltip: l10n.gateRevokePlate,
                    icon: const Icon(Icons.delete),
                    onPressed: () => _confirmRevoke(
                      l10n.gateRevokePlate,
                      () => widget.repository.deletePlate(item['id'] as int),
                    ),
                  ),
                ),
              const Divider(height: 32),
              ListTile(
                title: Text(l10n.gateFaceTitle),
                subtitle: Text(
                  face == null
                      ? l10n.gateNotRegistered
                      : _statusText(
                          l10n,
                          '${face['status']}',
                          '${face['review_note'] ?? ''}',
                        ),
                ),
              ),
              const SizedBox(height: 8),
              Text(l10n.gateRetentionNotice),
              const SizedBox(height: 12),
              AdaptiveFilledButton(
                busy: busy,
                onPressed: busy
                    ? null
                    : () async {
                        final photo = await (widget.picker ?? ImagePicker())
                            .pickImage(
                              source: ImageSource.camera,
                              // Selfie flow: the resident photographs their
                              // own face, not the room behind the phone.
                              preferredCameraDevice: CameraDevice.front,
                            );
                        if (photo != null) {
                          await _run(
                            () => widget.repository.submitFace(photo.path),
                          );
                        }
                      },
                child: Text(l10n.gateCaptureFace),
              ),
              if (face != null) ...[
                const SizedBox(height: 8),
                AdaptiveTextButton(
                  onPressed: () => _confirmRevoke(
                    l10n.gateRevokeFace,
                    widget.repository.deleteFace,
                  ),
                  child: Text(l10n.gateRevokeFace),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _confirmRevoke(
    String title,
    Future<void> Function() action,
  ) async {
    final l10n = AppLocalizations.of(context)!;
    final confirmed = defaultTargetPlatform == TargetPlatform.iOS
        ? await showCupertinoDialog<bool>(
            context: context,
            builder: (context) => CupertinoAlertDialog(
              title: Text(title),
              content: Text(l10n.gateRevokeConfirmBody),
              actions: [
                CupertinoDialogAction(
                  isDefaultAction: true,
                  onPressed: () => Navigator.pop(context, false),
                  child: Text(l10n.commonCancel),
                ),
                CupertinoDialogAction(
                  isDestructiveAction: true,
                  onPressed: () => Navigator.pop(context, true),
                  child: Text(l10n.gateRevokeConfirm),
                ),
              ],
            ),
          )
        : await showDialog<bool>(
            context: context,
            builder: (context) => AlertDialog(
              title: Text(title),
              content: Text(l10n.gateRevokeConfirmBody),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context, false),
                  child: Text(l10n.commonCancel),
                ),
                FilledButton(
                  onPressed: () => Navigator.pop(context, true),
                  child: Text(l10n.gateRevokeConfirm),
                ),
              ],
            ),
          );
    if (confirmed == true) await _run(action);
  }
}

String _statusText(AppLocalizations l10n, String status, String note) =>
    switch (status) {
      'PENDING' => l10n.gateStatusPending,
      'APPROVED' => l10n.gateStatusApproved,
      'REJECTED' => l10n.gateStatusRejected(note),
      'EXPIRED' => l10n.gateStatusExpired,
      _ => l10n.gateStatusUnknown,
    };
