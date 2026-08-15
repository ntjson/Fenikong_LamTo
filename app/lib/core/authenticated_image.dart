import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../l10n/app_localizations.dart';
import 'providers.dart';

/// Fetches a signed relative URL through the shared Dio (knox token attached)
/// and renders the bytes. Image.network cannot carry our auth header.
///
/// The GET is memoized per [url]: parent rebuilds with the same URL reuse the
/// in-flight or completed future (no re-fetch). On failure, an explicit retry
/// control clears the memoized future and re-issues the GET.
class AuthenticatedImage extends ConsumerStatefulWidget {
  const AuthenticatedImage(
    this.url, {
    this.width,
    this.height,
    this.semanticLabel,
    super.key,
  });

  final String url;
  final double? width;
  final double? height;

  /// Announced for the image; loading and error states prefix it to their
  /// own wording so evidence photos are never silence in a screen reader.
  final String? semanticLabel;

  @override
  ConsumerState<AuthenticatedImage> createState() => _AuthenticatedImageState();
}

class _AuthenticatedImageState extends ConsumerState<AuthenticatedImage> {
  Future<Response<List<int>>>? _future;
  String? _url;

  /// Bumped on each explicit retry so FutureBuilder sees a new future.
  int _retryToken = 0;

  Future<Response<List<int>>> _startFetch(Dio dio, String url) {
    return dio.get<List<int>>(
      url,
      options: Options(responseType: ResponseType.bytes),
    );
  }

  Future<Response<List<int>>> _futureFor(Dio dio) {
    if (_future == null || _url != widget.url) {
      _url = widget.url;
      _future = _startFetch(dio, widget.url);
    }
    return _future!;
  }

  void _retry() {
    setState(() {
      _future = null;
      _url = null;
      _retryToken++;
    });
  }

  @override
  void didUpdateWidget(covariant AuthenticatedImage oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.url != widget.url) {
      _future = null;
      _url = null;
    }
  }

  /// "{label}. {state}" when a label exists; just the state otherwise.
  String _stateLabel(String state) {
    final label = widget.semanticLabel;
    return label == null ? state : '$label. $state';
  }

  @override
  Widget build(BuildContext context) {
    final dio = ref.watch(dioProvider);
    final l10n = AppLocalizations.of(context);
    return FutureBuilder<Response<List<int>>>(
      // ValueKey forces FutureBuilder to re-subscribe after explicit retry.
      key: ValueKey<int>(_retryToken),
      future: _futureFor(dio),
      builder: (context, snapshot) {
        if (snapshot.hasData && snapshot.data?.data != null) {
          final data = snapshot.data!.data!;
          // Dio already hands back a Uint8List for ResponseType.bytes; reusing
          // it keeps MemoryImage's cache key stable across rebuilds (a fresh
          // copy per build would force a full JPEG re-decode every frame).
          final bytes = data is Uint8List ? data : Uint8List.fromList(data);
          final width = widget.width;
          return Image.memory(
            bytes,
            width: width,
            height: widget.height,
            fit: BoxFit.cover,
            semanticLabel: widget.semanticLabel,
            // Decode at display size, not the server's full resolution: a
            // 2048px photo decoded for a 96px thumb costs ~16 MB and jank.
            cacheWidth: width == null
                ? null
                : (width * MediaQuery.devicePixelRatioOf(context)).round(),
            gaplessPlayback: true,
          );
        }
        if (snapshot.hasError) {
          final retryLabel = l10n?.commonRetry ?? 'Retry';
          return Semantics(
            liveRegion: true,
            label: _stateLabel(
              l10n?.photoLoadFailed ?? 'The photo could not be loaded.',
            ),
            child: SizedBox(
              width: widget.width,
              height: widget.height,
              child: Center(
                child: IconButton(
                  key: const Key('authenticated_image_retry'),
                  tooltip: retryLabel,
                  icon: const Icon(Icons.refresh),
                  onPressed: _retry,
                ),
              ),
            ),
          );
        }
        return Semantics(
          label: _stateLabel(l10n?.photoLoading ?? 'Loading photo…'),
          child: SizedBox(
            width: widget.width,
            height: widget.height,
            child: const Center(child: CircularProgressIndicator.adaptive()),
          ),
        );
      },
    );
  }
}
