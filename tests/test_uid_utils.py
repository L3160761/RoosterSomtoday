import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from uid_utils import normalize_tag_uid


class NormalizeTagUidTests(unittest.TestCase):
    def test_normalizes_hex_uid(self):
        self.assertEqual(normalize_tag_uid("04:a1-b2 3c"), "04A1B23C")

    def test_converts_decimal_byte_notation(self):
        self.assertEqual(normalize_tag_uid("84-122-51-19"), "547A3313")

    def test_accepts_seven_byte_uid(self):
        self.assertEqual(
            normalize_tag_uid("04:A1:B2:3C:4D:5E:6F"),
            "04A1B23C4D5E6F",
        )

    def test_rejects_invalid_uid(self):
        with self.assertRaises(ValueError):
            normalize_tag_uid("geen-uid")


if __name__ == "__main__":
    unittest.main()
