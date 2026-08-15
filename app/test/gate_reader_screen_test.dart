import 'dart:io';

import 'package:camera/camera.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lamto/core/failure.dart';
import 'package:lamto/features/gate/reader/gate_reader_screen.dart';
import 'package:lamto/features/gate/reader/reader_credential_store.dart';
import 'package:lamto/features/gate/reader/reader_repository.dart';
import 'package:lamto/l10n/app_localizations_vi.dart';
import 'package:shared_preferences/shared_preferences.dart';

class FakeReader implements ReaderApi {
  FakeReader({this.matched = true, this.error, this.deviceDirection = 'ENTRY'});
  final bool matched;
  final Object? error;
  final String deviceDirection;
  String? plate;
  String? facePath;
  int deviceCalls = 0;
  @override
  Future<ReaderDevice> getDevice() async {
    deviceCalls++;
    return ReaderDevice.fromJson({
      'label': 'North',
      'direction': deviceDirection,
    });
  }

  @override
  Future<ReaderResult> recognizeFace(String path) async {
    facePath = path;
    if (error != null) throw error!;
    return ReaderResult.fromJson({
      'matched': matched,
      'display_name': 'An',
      'unit_label': '101',
      'direction': 'ENTRY',
    });
  }

  @override
  Future<ReaderResult> recognizePlate(String value) async {
    plate = value;
    if (error != null) throw error!;
    return ReaderResult.fromJson({
      'matched': matched,
      'display_name': 'An',
      'unit_label': '101',
      'direction': 'ENTRY',
    });
  }
}

class MemoryStore extends ReaderCredentialStore {
  MemoryStore([this.value]);
  String? value;
  @override
  Future<String?> read() async => value;
  @override
  Future<void> write(String value) async => this.value = value;
  @override
  Future<void> clear() async => value = null;
}

class FakeCamera implements ReaderCamera {
  FakeCamera(this.path);
  final String path;
  int captures = 0;
  @override
  Widget get preview =>
      const ColoredBox(key: Key('camera-preview'), color: Colors.black);
  @override
  Future<XFile> capture() async {
    captures++;
    return XFile(path);
  }

  @override
  Future<void> dispose() async {}
}

void main() {
  setUp(() => SharedPreferences.setMockInitialValues({}));

  testWidgets('secure credential is persisted and can be cleared', (
    tester,
  ) async {
    final store = MemoryStore();
    await tester.pumpWidget(
      MaterialApp(
        home: GateReaderScreen(
          repositoryFor: (_) => FakeReader(),
          camera: FakeCamera('/tmp/unused'),
          store: store,
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.enterText(
      find.byKey(const Key('reader-credential')),
      ' secret ',
    );
    await tester.tap(find.text('Kích hoạt đầu đọc'));
    await tester.pump();
    expect(store.value, 'secret');
    expect(find.byKey(const Key('camera-preview')), findsOneWidget);
    expect(find.text('ENTRY'), findsOneWidget);
    await tester.tap(find.text('Xóa mã thiết bị'));
    await tester.pump();
    expect(store.value, isNull);
  });

  testWidgets('OCR submission shows matched result and deletes capture', (
    tester,
  ) async {
    final file = File('${Directory.systemTemp.path}/gate-reader-plate.jpg')
      ..writeAsBytesSync([1]);
    final camera = FakeCamera(file.path);
    final reader = FakeReader();
    await tester.pumpWidget(
      MaterialApp(
        home: GateReaderScreen(
          repositoryFor: (_) => reader,
          camera: camera,
          store: MemoryStore('token'),
          ocr: (_) async => '51F12345',
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Quét biển số'));
    await tester.pumpAndSettle();
    expect(reader.plate, '51F12345');
    expect(find.textContaining('An'), findsOneWidget);
    expect(file.existsSync(), isFalse);
  });

  testWidgets('unmatched face is shown and network failure is never queued', (
    tester,
  ) async {
    final file = File('${Directory.systemTemp.path}/gate-reader-face.jpg')
      ..writeAsBytesSync([1]);
    final camera = FakeCamera(file.path);
    final reader = FakeReader(
      error: DioException(requestOptions: RequestOptions()),
    );
    await tester.pumpWidget(
      MaterialApp(
        home: GateReaderScreen(
          repositoryFor: (_) => reader,
          camera: camera,
          store: MemoryStore('token'),
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Quét khuôn mặt'));
    await tester.pumpAndSettle();
    expect(find.textContaining('chưa được lưu'), findsOneWidget);
    expect(camera.captures, 1);
    expect(file.existsSync(), isFalse);
  });

  testWidgets('unmatched recognition is shown', (tester) async {
    final file = File('${Directory.systemTemp.path}/gate-reader-unmatched.jpg')
      ..writeAsBytesSync([1]);
    await tester.pumpWidget(
      MaterialApp(
        home: GateReaderScreen(
          repositoryFor: (_) => FakeReader(matched: false),
          camera: FakeCamera(file.path),
          store: MemoryStore('token'),
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Quét khuôn mặt'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Không nhận diện được'), findsOneWidget);
    expect(file.existsSync(), isFalse);
  });

  testWidgets('an unusable server URL blocks activation before any request', (
    tester,
  ) async {
    final reader = FakeReader();
    await tester.pumpWidget(
      MaterialApp(
        home: GateReaderScreen(
          repositoryFor: (_) => reader,
          camera: FakeCamera('/tmp/unused'),
          store: MemoryStore(),
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.enterText(
      find.byKey(const Key('reader-base-url')),
      'localhost:8000',
    );
    await tester.enterText(
      find.byKey(const Key('reader-credential')),
      'secret',
    );
    await tester.tap(find.text('Kích hoạt đầu đọc'));
    await tester.pumpAndSettle();
    expect(reader.deviceCalls, 0);
    expect(find.textContaining('không hợp lệ'), findsOneWidget);
    expect(find.byKey(const Key('camera-preview')), findsNothing);
  });

  testWidgets('server URL is normalized, applied, and restored on relaunch', (
    tester,
  ) async {
    final applied = <String>[];
    await tester.pumpWidget(
      MaterialApp(
        home: GateReaderScreen(
          repositoryFor: (_) => FakeReader(),
          camera: FakeCamera('/tmp/unused'),
          store: MemoryStore(),
          onBaseUrl: applied.add,
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.enterText(
      find.byKey(const Key('reader-base-url')),
      '  http://10.0.2.2:8000/  ',
    );
    await tester.enterText(
      find.byKey(const Key('reader-credential')),
      'secret',
    );
    await tester.tap(find.text('Kích hoạt đầu đọc'));
    await tester.pumpAndSettle();

    expect(applied.last, 'http://10.0.2.2:8000');
    expect(find.byKey(const Key('camera-preview')), findsOneWidget);

    // A relaunch must reuse the saved host, not the compile-time default.
    // Unmount first: pumping the same widget type in place would reuse the
    // existing State and never re-run bootstrap.
    await tester.pumpWidget(const SizedBox());
    await tester.pumpAndSettle();
    final relaunched = <String>[];
    await tester.pumpWidget(
      MaterialApp(
        home: GateReaderScreen(
          repositoryFor: (_) => FakeReader(),
          camera: FakeCamera('/tmp/unused'),
          store: MemoryStore(),
          onBaseUrl: relaunched.add,
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(relaunched, contains('http://10.0.2.2:8000'));
  });

  test('reader errors map every stable face code distinctly', () {
    final codes = [
      'gate_no_face_detected',
      'gate_multiple_faces',
      'gate_face_too_small',
      'gate_face_too_blurry',
      'gate_face_unusable',
      'gate_photo_rejected',
      'gate_face_upload_too_large',
    ];
    expect(
      codes
          .map(
            (code) => failureMessage(
              Failure.fromObject(_problem(code)),
              AppLocalizationsVi(),
            ),
          )
          .toSet(),
      hasLength(codes.length),
    );
  });

  testWidgets('reader displays authenticated server direction', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: GateReaderScreen(
          repositoryFor: (_) => FakeReader(deviceDirection: 'EXIT'),
          camera: FakeCamera('/tmp/unused'),
          store: MemoryStore('token'),
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('EXIT'), findsOneWidget);
    expect(find.text('ENTRY'), findsNothing);
  });
}

DioException _problem(String code) => DioException(
  requestOptions: RequestOptions(),
  response: Response(requestOptions: RequestOptions(), data: {'code': code}),
);
