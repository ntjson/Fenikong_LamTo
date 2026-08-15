import pytest

from lamto.gate.plates import PlateFormatError, normalize_plate


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("51F-123.45", "51F12345"),
        ("  51f 123 45 ", "51F12345"),
        ("29-A1 234.56", "29A123456"),
        ("59X1-99999", "59X199999"),
        ("51F12345", "51F12345"),
    ],
)
def test_normalizes_to_uppercase_alphanumeric(raw, expected):
    assert normalize_plate(raw) == expected


@pytest.mark.parametrize("raw", ["", "   ", "!!!", "51F", "-.-", "51F1234567890123"])
def test_rejects_plates_without_usable_content(raw):
    with pytest.raises(PlateFormatError):
        normalize_plate(raw)


def test_rejects_none_without_raising_type_error():
    with pytest.raises(PlateFormatError):
        normalize_plate(None)
