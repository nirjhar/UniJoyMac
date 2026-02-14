#!/usr/bin/env python3
"""Convert an Avro .avrolayout file to macOS .keylayout XML."""

from __future__ import annotations

import argparse
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path


# macOS ANSI key codes used in .keylayout files.
KEYCODE_BY_AVRO_KEY = {
    "OEM3": 50,   # ` ~
    "1": 18,
    "2": 19,
    "3": 20,
    "4": 21,
    "5": 23,
    "6": 22,
    "7": 26,
    "8": 28,
    "9": 25,
    "0": 29,
    "MINUS": 27,
    "PLUS": 24,
    "Q": 12,
    "W": 13,
    "E": 14,
    "R": 15,
    "T": 17,
    "Y": 16,
    "U": 32,
    "I": 34,
    "O": 31,
    "P": 35,
    "OEM4": 33,   # [ {
    "OEM6": 30,   # ] }
    "OEM5": 42,   # \\ |
    "A": 0,
    "S": 1,
    "D": 2,
    "F": 3,
    "G": 5,
    "H": 4,
    "J": 38,
    "K": 40,
    "L": 37,
    "OEM1": 41,   # ; :
    "OEM7": 39,   # ' "
    "Z": 6,
    "X": 7,
    "C": 8,
    "V": 9,
    "B": 11,
    "N": 45,
    "M": 46,
    "COMMA": 43,
    "PERIOD": 47,
    "OEM2": 44,   # / ?
}

STATE_BY_AVRO_SUFFIX = {
    "Normal": "normal",
    "Shift": "shift",
    "AltGr": "option",
    "ShiftAltGr": "option_shift",
}

MODIFIER_ORDER = ["normal", "shift", "option", "option_shift"]


def parse_avro_keydata(avro_path: Path) -> dict[str, dict[str, str]]:
    raw = avro_path.read_text(encoding="utf-8")
    keydata_match = re.search(r"<KeyData>(.*?)</KeyData>", raw, flags=re.DOTALL)
    if not keydata_match:
        raise ValueError("No <KeyData> section found in avrolayout file")

    keydata_text = keydata_match.group(1)

    mapping: dict[str, dict[str, str]] = {
        key: {state: "" for state in MODIFIER_ORDER}
        for key in KEYCODE_BY_AVRO_KEY
    }

    field_pattern = re.compile(
        r"<([A-Za-z0-9]+)_(Normal|Shift|AltGr|ShiftAltGr)>(.*?)</\1_\2>",
        flags=re.DOTALL,
    )
    cdata_pattern = re.compile(r"^<!\[CDATA\[(.*)\]\]>$", flags=re.DOTALL)

    for match in field_pattern.finditer(keydata_text):
        avro_key, suffix, body = match.groups()
        if avro_key not in KEYCODE_BY_AVRO_KEY:
            continue

        state = STATE_BY_AVRO_SUFFIX[suffix]
        value = body.strip()
        cdata_match = cdata_pattern.match(value)
        if cdata_match:
            value = cdata_match.group(1)
        mapping[avro_key][state] = unicodedata.normalize("NFC", value)

    return mapping


def indent_xml(elem: ET.Element, level: int = 0) -> None:
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for child in elem:
            indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i + "  "
        if not elem[-1].tail or not elem[-1].tail.strip():
            elem[-1].tail = i
    elif level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i


def build_keylayout_xml(
    mapping: dict[str, dict[str, str]],
    layout_name: str,
    keyboard_id: int,
    group: int,
) -> str:
    keyboard = ET.Element(
        "keyboard",
        {
            "group": str(group),
            "id": str(keyboard_id),
            "name": layout_name,
            "maxout": "4",
        },
    )

    layouts = ET.SubElement(keyboard, "layouts")
    ET.SubElement(layouts, "layout", {"first": "0", "last": "0", "mapSet": "0", "modifiers": "0"})

    modifier_map = ET.SubElement(keyboard, "modifierMap", {"id": "0", "defaultIndex": "0"})
    ET.SubElement(modifier_map, "keyMapSelect", {"mapIndex": "0"})
    ET.SubElement(modifier_map, "keyMapSelect", {"mapIndex": "1"})
    ET.SubElement(modifier_map[0], "modifier", {"keys": ""})
    ET.SubElement(modifier_map[1], "modifier", {"keys": "anyShift"})
    keymap_select_2 = ET.SubElement(modifier_map, "keyMapSelect", {"mapIndex": "2"})
    ET.SubElement(keymap_select_2, "modifier", {"keys": "anyOption"})
    keymap_select_3 = ET.SubElement(modifier_map, "keyMapSelect", {"mapIndex": "3"})
    ET.SubElement(keymap_select_3, "modifier", {"keys": "anyShift anyOption"})

    key_map_set = ET.SubElement(keyboard, "keyMapSet", {"id": "0"})
    sorted_keys = sorted(KEYCODE_BY_AVRO_KEY.items(), key=lambda item: item[1])

    for index, state in enumerate(MODIFIER_ORDER):
        key_map = ET.SubElement(key_map_set, "keyMap", {"index": str(index)})
        for avro_key, keycode in sorted_keys:
            output = mapping.get(avro_key, {}).get(state, "")
            ET.SubElement(key_map, "key", {"code": str(keycode), "output": output})

    indent_xml(keyboard)
    xml_body = ET.tostring(keyboard, encoding="unicode")
    header = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!DOCTYPE keyboard SYSTEM "file://localhost/System/Library/DTDs/KeyboardLayout.dtd">\n'
    )
    return header + xml_body + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert Avro .avrolayout to macOS .keylayout")
    parser.add_argument("input", type=Path, help="Path to ub.avrolayout")
    parser.add_argument("output", type=Path, help="Path to output .keylayout")
    parser.add_argument("--layout-name", default="UniJoyMac", help="Layout name in keylayout")
    parser.add_argument("--keyboard-id", type=int, default=8801, help="Integer keyboard id")
    parser.add_argument("--group", type=int, default=126, help="Keyboard group id")
    args = parser.parse_args()

    mapping = parse_avro_keydata(args.input)
    xml_text = build_keylayout_xml(mapping, args.layout_name, args.keyboard_id, args.group)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(xml_text, encoding="utf-8")


if __name__ == "__main__":
    main()
