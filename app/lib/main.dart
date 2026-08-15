import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:camera/camera.dart';
import 'package:dio/dio.dart';

import 'app.dart';
import 'core/config.dart';
import 'features/gate/reader/gate_reader_screen.dart';
import 'features/gate/reader/reader_repository.dart';

Future<void> main() async {
  const readerMode = bool.fromEnvironment('GATE_READER_MODE');
  if (!readerMode) {
    runApp(const ProviderScope(child: LamToApp()));
    return;
  }
  WidgetsFlutterBinding.ensureInitialized();
  final cameras = await availableCameras();
  final controller = CameraController(
    cameras.first,
    ResolutionPreset.medium,
    enableAudio: false,
  );
  await controller.initialize();
  final dio = Dio(BaseOptions(baseUrl: apiBaseUrl));
  runApp(
    MaterialApp(
      home: GateReaderScreen(
        camera: CameraReader(controller),
        repositoryFor: (credential) => ReaderRepository(dio, credential),
        onBaseUrl: (url) => dio.options.baseUrl = url,
      ),
    ),
  );
}
