final _nonAlnum = RegExp(r'[^A-Z0-9]');
String normalizePlateText(String raw) =>
    raw.toUpperCase().replaceAll(_nonAlnum, '');
bool isPlausiblePlate(String value) => value.length >= 5 && value.length <= 12;
