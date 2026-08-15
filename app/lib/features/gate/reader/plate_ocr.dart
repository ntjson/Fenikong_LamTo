import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';
import '../plate_text.dart';

final _plateShape = RegExp(r'^[0-9]{2}[A-Z]{1,2}[0-9]{4,6}$');
String? bestPlateFromLines(List<String> lines, {bool joinAdjacent = false}) {
  final candidates = <String>[];
  for (var i = 0; i < lines.length; i++) {
    candidates.add(normalizePlateText(lines[i]));
    if (joinAdjacent && i + 1 < lines.length) {
      candidates.add(normalizePlateText('${lines[i]}${lines[i + 1]}'));
    }
  }
  final plausible = candidates.where(isPlausiblePlate);
  return plausible.where(_plateShape.hasMatch).firstOrNull;
}

Future<String?> extractPlate(String path) async {
  final recognizer = TextRecognizer(script: TextRecognitionScript.latin);
  try {
    final text = await recognizer.processImage(InputImage.fromFilePath(path));
    for (final block in text.blocks) {
      final plate = bestPlateFromLines(
        block.lines.map((x) => x.text).toList(),
        joinAdjacent: true,
      );
      if (plate != null) return plate;
    }
    return null;
  } finally {
    await recognizer.close();
  }
}
