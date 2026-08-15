import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/core/authenticated_image.dart';
import 'package:lamto/core/providers.dart';
import 'package:lamto/l10n/app_localizations.dart';

/// Minimal 1x1 PNG so Image.memory can decode when the future completes.
final _pngBytes = Uint8List.fromList(<int>[
  0x89,
  0x50,
  0x4e,
  0x47,
  0x0d,
  0x0a,
  0x1a,
  0x0a,
  0x00,
  0x00,
  0x00,
  0x0d,
  0x49,
  0x48,
  0x44,
  0x52,
  0x00,
  0x00,
  0x00,
  0x01,
  0x00,
  0x00,
  0x00,
  0x01,
  0x08,
  0x06,
  0x00,
  0x00,
  0x00,
  0x1f,
  0x15,
  0xc4,
  0x89,
  0x00,
  0x00,
  0x00,
  0x0a,
  0x49,
  0x44,
  0x41,
  0x54,
  0x78,
  0x9c,
  0x63,
  0x00,
  0x01,
  0x00,
  0x00,
  0x05,
  0x00,
  0x01,
  0x0d,
  0x0a,
  0x2d,
  0xb4,
  0x00,
  0x00,
  0x00,
  0x00,
  0x49,
  0x45,
  0x4e,
  0x44,
  0xae,
  0x42,
  0x60,
  0x82,
]);

/// Counts GETs through the real Dio path used by [AuthenticatedImage].
class _CountingAdapter implements HttpClientAdapter {
  int getCount = 0;
  final paths = <String>[];

  /// When non-empty, the next fetch fails once then succeeds.
  int failNext = 0;

  @override
  void close({bool force = false}) {}

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    getCount++;
    paths.add(options.path);
    if (failNext > 0) {
      failNext--;
      throw DioException(
        requestOptions: options,
        type: DioExceptionType.connectionError,
        message: 'simulated failure',
      );
    }
    return ResponseBody.fromBytes(
      _pngBytes,
      200,
      headers: {
        Headers.contentTypeHeader: ['image/png'],
      },
    );
  }
}

void main() {
  late Dio dio;
  late _CountingAdapter adapter;
  late ProviderContainer container;

  setUp(() {
    adapter = _CountingAdapter();
    dio = Dio(BaseOptions(baseUrl: 'http://x'));
    dio.httpClientAdapter = adapter;
    container = ProviderContainer(
      overrides: [dioProvider.overrideWith((ref) => dio)],
    );
  });

  tearDown(() => container.dispose());

  Widget host({required Widget child}) {
    return UncontrolledProviderScope(
      container: container,
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: const Locale('en'),
        home: Scaffold(body: child),
      ),
    );
  }

  testWidgets('rebuild with same URL does not re-issue GET', (tester) async {
    late StateSetter rebuild;
    await tester.pumpWidget(
      host(
        child: StatefulBuilder(
          builder: (context, setState) {
            rebuild = setState;
            return const AuthenticatedImage(
              '/api/v1/documents/tok',
              width: 40,
              height: 40,
            );
          },
        ),
      ),
    );
    await tester.idle();
    expect(adapter.getCount, 1);
    expect(adapter.paths, ['/api/v1/documents/tok']);

    rebuild(() {});
    await tester.pump();
    await tester.idle();
    expect(adapter.getCount, 1);
  });

  testWidgets('different URL starts a new GET', (tester) async {
    var url = '/api/v1/documents/a';
    late StateSetter rebuild;
    await tester.pumpWidget(
      host(
        child: StatefulBuilder(
          builder: (context, setState) {
            rebuild = setState;
            return AuthenticatedImage(url, width: 40, height: 40);
          },
        ),
      ),
    );
    await tester.idle();
    expect(adapter.getCount, 1);

    url = '/api/v1/documents/b';
    rebuild(() {});
    await tester.pump();
    await tester.idle();
    expect(adapter.getCount, 2);
    expect(adapter.paths, ['/api/v1/documents/a', '/api/v1/documents/b']);
  });

  testWidgets('exposes the semantic label on the loaded image', (tester) async {
    final semantics = tester.ensureSemantics();
    await tester.pumpWidget(
      host(
        child: const AuthenticatedImage(
          '/api/v1/documents/tok',
          width: 40,
          height: 40,
          semanticLabel: 'Ảnh sau khi sửa',
        ),
      ),
    );
    // Loading announces the label with the loading wording.
    expect(
      find.bySemanticsLabel('Ảnh sau khi sửa. Loading photo…'),
      findsOneWidget,
    );

    await tester.idle();
    await tester.pump();
    expect(find.bySemanticsLabel('Ảnh sau khi sửa'), findsOneWidget);
    semantics.dispose();
  });

  testWidgets('error state announces the label with failure wording', (
    tester,
  ) async {
    final semantics = tester.ensureSemantics();
    adapter.failNext = 1;
    await tester.pumpWidget(
      host(
        child: const AuthenticatedImage(
          '/api/v1/documents/tok',
          width: 40,
          height: 40,
          semanticLabel: 'Ảnh trước khi sửa',
        ),
      ),
    );
    await tester.idle();
    await tester.pump();

    expect(
      find.bySemanticsLabel(
        'Ảnh trước khi sửa. The photo could not be loaded.',
      ),
      findsOneWidget,
    );
    semantics.dispose();
  });

  testWidgets('explicit retry after error re-issues GET and shows image', (
    tester,
  ) async {
    adapter.failNext = 1;
    await tester.pumpWidget(
      host(
        child: const AuthenticatedImage(
          '/api/v1/documents/retry-me',
          width: 40,
          height: 40,
        ),
      ),
    );
    await tester.idle();
    await tester.pump();
    expect(adapter.getCount, 1);
    expect(find.byKey(const Key('authenticated_image_retry')), findsOneWidget);

    await tester.tap(find.byKey(const Key('authenticated_image_retry')));
    await tester.pump();
    await tester.idle();
    await tester.pump();

    expect(adapter.getCount, 2);
    expect(find.byKey(const Key('authenticated_image_retry')), findsNothing);
    expect(find.byType(Image), findsOneWidget);
  });
}
