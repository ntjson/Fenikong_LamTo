import 'dart:convert';
import 'dart:io';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/features/reports/reports_repository.dart';
import 'package:mocktail/mocktail.dart';

class _MockAdapter extends Mock implements HttpClientAdapter {}

ResponseBody _json(int status, Object body) => ResponseBody.fromString(
  jsonEncode(body),
  status,
  headers: {
    Headers.contentTypeHeader: [Headers.jsonContentType],
  },
);

void main() {
  setUpAll(() => registerFallbackValue(RequestOptions(path: '/')));

  late _MockAdapter adapter;
  late DioReportsRepository repo;
  late RequestOptions lastRequest;

  setUp(() {
    adapter = _MockAdapter();
    final dio = Dio(BaseOptions(baseUrl: 'http://x'));
    dio.httpClientAdapter = adapter;
    repo = DioReportsRepository(dio);
  });

  void answerWith(int status, Object body) {
    when(() => adapter.fetch(any(), any(), any())).thenAnswer((inv) async {
      lastRequest = inv.positionalArguments[0] as RequestOptions;
      return _json(status, body);
    });
  }

  test(
    'createReport posts client_ref/text/location_id and parses summary',
    () async {
      answerWith(201, {
        'id': 5,
        'text': 'Leak',
        'status': 'SUBMITTED',
        'is_private': false,
        'location_path_snapshot': 'B / Hall',
        'created_at': '2026-07-17T00:00:00Z',
      });
      final summary = await repo.createReport(
        clientRef: 'ref-1',
        text: 'Leak',
        locationId: 3,
      );
      expect(summary.id, 5);
      expect(lastRequest.path, '/api/v1/reports');
      final sent = lastRequest.data;
      final map = sent is String ? jsonDecode(sent) : sent;
      expect(map['client_ref'], 'ref-1');
      expect(map['text'], 'Leak');
      expect(map['location_id'], 3);
    },
  );

  test('uploadPhoto sends multipart field "photo"', () async {
    answerWith(201, {
      'id': 9,
      'filename': 'p.jpg',
      'sha256': 'aa',
      'download_url': '/api/v1/documents/tok',
    });
    // A real temp file so MultipartFile.fromFile can read it.
    final photo = await repo.uploadPhoto(
      reportId: 5,
      path: _writeTempJpeg(),
      filename: 'p.jpg',
    );
    expect(photo.id, 9);
    expect(lastRequest.path, '/api/v1/reports/5/photos');
    expect(lastRequest.data, isA<FormData>());
    final form = lastRequest.data as FormData;
    expect(form.files.single.key, 'photo');
  });

  test('cursorFromNext extracts the DRF cursor param', () {
    expect(cursorFromNext(null), isNull);
    expect(
      cursorFromNext('http://x/api/v1/reports?cursor=cD0yMDI2'),
      'cD0yMDI2',
    );
  });

  // Amendment 13: adapter-level HTTP 200 idempotent create replay (not a fake repo).
  test(
    'createReport accepts HTTP 200 idempotent replay of same client_ref',
    () async {
      var calls = 0;
      when(() => adapter.fetch(any(), any(), any())).thenAnswer((inv) async {
        lastRequest = inv.positionalArguments[0] as RequestOptions;
        calls++;
        final body = {
          'id': 5,
          'text': 'Leak',
          'status': 'SUBMITTED',
          'is_private': false,
          'location_path_snapshot': 'B / Hall',
          'created_at': '2026-07-17T00:00:00Z',
        };
        return _json(calls == 1 ? 201 : 200, body);
      });
      final first = await repo.createReport(
        clientRef: 'ref-1',
        text: 'Leak',
        locationId: 3,
      );
      final second = await repo.createReport(
        clientRef: 'ref-1',
        text: 'Leak',
        locationId: 3,
      );
      expect(first.id, 5);
      expect(second.id, 5);
      expect(calls, 2);
    },
  );
}

String _writeTempJpeg() {
  final file = File(
    '${Directory.systemTemp.createTempSync('lamto').path}/p.jpg',
  )..writeAsBytesSync([0xff, 0xd8, 0xff, 0xe0]);
  return file.path;
}
