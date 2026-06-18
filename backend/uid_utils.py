"""Canonical formatting and validation for RFID/NFC tag UIDs."""

import re

_DECIMAL_UID = re.compile(
    r"^\s*\d{1,3}(?:\s*[-,]\s*\d{1,3}){3,9}\s*$"
)
_ALLOWED_UID_LENGTHS = {4, 7, 10}


def normalize_tag_uid(value: str) -> str:
    """Return a UID as uppercase hexadecimal without separators.

    Accepted inputs include 04A1B23C, 04:A1:B2:3C and decimal byte
    notation such as 4-161-178-60. No tag memory is read or written.
    """
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Tag UID is verplicht")

    value = value.strip()

    if _DECIMAL_UID.fullmatch(value):
        parts = re.split(r"\s*[-,]\s*", value)
        if len(parts) not in _ALLOWED_UID_LENGTHS:
            raise ValueError("Een UID moet 4, 7 of 10 bytes bevatten")

        byte_values = [int(part, 10) for part in parts]
        if any(byte_value > 255 for byte_value in byte_values):
            raise ValueError("Elke decimale UID-byte moet tussen 0 en 255 liggen")

        return "".join(f"{byte_value:02X}" for byte_value in byte_values)

    compact = re.sub(r"[\s:.-]", "", value).upper()
    if not re.fullmatch(r"[0-9A-F]+", compact):
        raise ValueError("Tag UID moet uit hexadecimale bytes bestaan")
    if len(compact) % 2 != 0 or len(compact) // 2 not in _ALLOWED_UID_LENGTHS:
        raise ValueError("Een UID moet 4, 7 of 10 bytes bevatten")

    return compact
