import 'dart:io';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../core/api_base_url.dart';
import '../../../core/failure.dart';
import '../../../l10n/app_localizations.dart';
import '../../../l10n/app_localizations_vi.dart';
import '../../../theme.dart';
import 'plate_ocr.dart';
import 'reader_credential_store.dart';
import 'reader_repository.dart';

abstract class ReaderCamera {
  Widget get preview;
  Future<XFile> capture();
  Future<void> dispose();
}

class CameraReader implements ReaderCamera {
  CameraReader(this.controller);
  final CameraController controller;
  @override
  Widget get preview => CameraPreview(controller);
  @override
  Future<XFile> capture() => controller.takePicture();
  @override
  Future<void> dispose() => controller.dispose();
}

class GateReaderScreen extends StatefulWidget {
  const GateReaderScreen({
    super.key,
    required this.repositoryFor,
    required this.camera,
    this.store,
    this.ocr = extractPlate,
    this.onBaseUrl,
  });
  final ReaderApi Function(String) repositoryFor;
  final ReaderCamera camera;
  final ReaderCredentialStore? store;
  final Future<String?> Function(String) ocr;

  /// Applies the operator-entered server URL. Reader mode runs without a
  /// [ProviderScope], so the host is pushed onto the caller's Dio instead of
  /// read from `apiBaseUrlProvider`.
  final void Function(String)? onBaseUrl;
  @override
  State<GateReaderScreen> createState() => _GateReaderScreenState();
}

class _GateReaderScreenState extends State<GateReaderScreen> {
  final credential = TextEditingController();
  final baseUrl = TextEditingController(text: defaultApiBaseUrl);
  String? token;
  String? direction;
  ReaderResult? result;
  String? message;
  bool busy = false;
  ReaderCredentialStore get store => widget.store ?? ReaderCredentialStore();
  AppLocalizations get l10n =>
      AppLocalizations.of(context) ?? AppLocalizationsVi();

  @override
  void initState() {
    super.initState();
    _bootstrap();
  }

  /// Restore the saved host before any stored credential is replayed, so a
  /// silent activation cannot run against a stale compile-time default.
  Future<void> _bootstrap() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = normalizeApiBaseUrl(
      prefs.getString(kApiBaseUrlPrefsKey) ?? '',
    );
    if (saved != null) {
      baseUrl.text = saved;
      widget.onBaseUrl?.call(saved);
    }
    final value = await store.read();
    if (value != null) await _activate(value, persist: false);
  }

  @override
  void dispose() {
    credential.dispose();
    baseUrl.dispose();
    widget.camera.dispose();
    super.dispose();
  }

  Future<void> _capture(bool face) async {
    final image = await widget.camera.capture();
    setState(() {
      busy = true;
      message = null;
      result = null;
    });
    try {
      final api = widget.repositoryFor(token!);
      final value = face
          ? await api.recognizeFace(image.path)
          : await widget.ocr(image.path).then((plate) {
              if (plate == null) {
                throw const FormatException();
              }
              return api.recognizePlate(plate);
            });
      if (mounted) setState(() => result = value);
    } on FormatException {
      if (mounted) {
        setState(() => message = l10n.gateReaderPlateUnreadable);
      }
    } catch (error) {
      if (mounted) {
        setState(
          () => message = failureMessage(Failure.fromObject(error), l10n),
        );
      }
    } finally {
      try {
        await File(image.path).delete();
      } on FileSystemException {
        /* Already removed. */
      }
      if (mounted) setState(() => busy = false);
    }
  }

  Future<void> _activate(String value, {bool persist = true}) async {
    final url = normalizeApiBaseUrl(baseUrl.text);
    if (url == null) {
      if (mounted) {
        setState(() => message = l10n.gateReaderInvalidUrl);
      }
      return;
    }
    widget.onBaseUrl?.call(url);
    if (persist) {
      // Saved on attempt, not on success: a reader pointed at a host that is
      // briefly down keeps its URL across a restart.
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(kApiBaseUrlPrefsKey, url);
    }
    try {
      final device = await widget.repositoryFor(value).getDevice();
      if (persist) {
        await store.write(value);
      }
      if (mounted) {
        setState(() {
          token = value;
          direction = device.direction;
          message = null;
        });
      }
    } catch (error) {
      if (mounted) {
        setState(
          () => message = failureMessage(Failure.fromObject(error), l10n),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = this.l10n;
    return Scaffold(
      appBar: AppBar(title: Text(l10n.gateReaderTitle)),
      body: token == null
          ? Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    TextField(
                      key: const Key('reader-base-url'),
                      controller: baseUrl,
                      keyboardType: TextInputType.url,
                      autocorrect: false,
                      enableSuggestions: false,
                      decoration: InputDecoration(
                        labelText: l10n.gateReaderServer,
                      ),
                    ),
                    TextField(
                      key: const Key('reader-credential'),
                      controller: credential,
                      obscureText: true,
                      decoration: InputDecoration(
                        labelText: l10n.gateReaderCredential,
                      ),
                    ),
                    FilledButton(
                      onPressed: () async {
                        final value = credential.text.trim();
                        if (value.isNotEmpty) {
                          await _activate(value);
                        }
                      },
                      child: busy
                          ? const CircularProgressIndicator.adaptive()
                          : Text(l10n.gateReaderActivate),
                    ),
                    if (message != null) Text(message!),
                  ],
                ),
              ),
            )
          : Column(
              children: [
                Expanded(
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      widget.camera.preview,
                      Align(
                        alignment: Alignment.topCenter,
                        child: SafeArea(child: Chip(label: Text(direction!))),
                      ),
                    ],
                  ),
                ),
                if (result != null)
                  Builder(
                    builder: (context) {
                      final colors = statusToneColors(
                        context,
                        result!.matched ? StatusTone.success : StatusTone.error,
                      );
                      return Card(
                        color: colors.bg,
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Text(
                            result!.matched
                                ? '${result!.name}\n${l10n.gateReaderUnit(result!.unit)}\n${result!.direction}'
                                : '${l10n.gateReaderNoMatch}\n${result!.direction}',
                            style: TextStyle(color: colors.fg),
                            textAlign: TextAlign.center,
                          ),
                        ),
                      );
                    },
                  ),
                if (message != null) Text(message!),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    FilledButton.icon(
                      onPressed: busy ? null : () => _capture(false),
                      icon: const Icon(Icons.directions_car),
                      label: Text(l10n.gateReaderScanPlate),
                    ),
                    const SizedBox(width: 8),
                    FilledButton.icon(
                      onPressed: busy ? null : () => _capture(true),
                      icon: const Icon(Icons.face),
                      label: Text(l10n.gateReaderScanFace),
                    ),
                  ],
                ),
                TextButton(
                  onPressed: () async {
                    await store.clear();
                    if (mounted) {
                      setState(() {
                        token = null;
                        result = null;
                      });
                    }
                  },
                  child: Text(l10n.gateReaderClearDevice),
                ),
              ],
            ),
    );
  }
}
