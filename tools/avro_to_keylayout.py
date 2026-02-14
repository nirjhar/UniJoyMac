#!/usr/bin/env python3
"""Convert an Avro .avrolayout file to macOS .keylayout XML."""

from __future__ import annotations

import argparse
import re
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

COMMAND_OUTPUT_BY_KEY = {
    "OEM3": "`",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "0": "0",
    "MINUS": "-",
    "PLUS": "=",
    "Q": "q",
    "W": "w",
    "E": "e",
    "R": "r",
    "T": "t",
    "Y": "y",
    "U": "u",
    "I": "i",
    "O": "o",
    "P": "p",
    "OEM4": "[",
    "OEM6": "]",
    "OEM5": "\\",
    "A": "a",
    "S": "s",
    "D": "d",
    "F": "f",
    "G": "g",
    "H": "h",
    "J": "j",
    "K": "k",
    "L": "l",
    "OEM1": ";",
    "OEM7": "'",
    "Z": "z",
    "X": "x",
    "C": "c",
    "V": "v",
    "B": "b",
    "N": "n",
    "M": "m",
    "COMMA": ",",
    "PERIOD": ".",
    "OEM2": "/",
}

SHIFTED_COMMAND_OUTPUT_BY_KEY = {
    "OEM3": "~",
    "1": "!",
    "2": "@",
    "3": "#",
    "4": "$",
    "5": "%",
    "6": "^",
    "7": "&",
    "8": "*",
    "9": "(",
    "0": ")",
    "MINUS": "_",
    "PLUS": "+",
    "Q": "Q",
    "W": "W",
    "E": "E",
    "R": "R",
    "T": "T",
    "Y": "Y",
    "U": "U",
    "I": "I",
    "O": "O",
    "P": "P",
    "OEM4": "{",
    "OEM6": "}",
    "OEM5": "|",
    "A": "A",
    "S": "S",
    "D": "D",
    "F": "F",
    "G": "G",
    "H": "H",
    "J": "J",
    "K": "K",
    "L": "L",
    "OEM1": ":",
    "OEM7": '"',
    "Z": "Z",
    "X": "X",
    "C": "C",
    "V": "V",
    "B": "B",
    "N": "N",
    "M": "M",
    "COMMA": "<",
    "PERIOD": ">",
    "OEM2": "?",
}

# UniJoy-style state machine for Bengali virama and dependent vowels.
# This improves conjunct behavior and allows typing independent vowels by
# pressing virama then the corresponding vowel sign.
VIRAMA = "্"
VIRAMA_STATE = "state_virama"
VIRAMA_ACTION_ID = "act_virama"
ACTION_ID_BY_OUTPUT = {
    "া": "act_sign_aa",
    "ি": "act_sign_i",
    "ী": "act_sign_ii",
    "ু": "act_sign_u",
    "ূ": "act_sign_uu",
    "ৃ": "act_sign_ri",
    "ে": "act_sign_e",
    "ো": "act_sign_o",
    "ৌ": "act_sign_ou",
    "ৈ": "act_sign_oi",
    VIRAMA: VIRAMA_ACTION_ID,
}
ACTION_OUTPUT_BY_ID = {
    "act_sign_aa": {"none": "া", VIRAMA_STATE: "আ"},
    "act_sign_i": {"none": "ি", VIRAMA_STATE: "ই"},
    "act_sign_ii": {"none": "ী", VIRAMA_STATE: "ঈ"},
    "act_sign_u": {"none": "ু", VIRAMA_STATE: "উ"},
    "act_sign_uu": {"none": "ূ", VIRAMA_STATE: "ঊ"},
    "act_sign_ri": {"none": "ৃ", VIRAMA_STATE: "ঋ"},
    "act_sign_e": {"none": "ে", VIRAMA_STATE: "এ"},
    "act_sign_o": {"none": "ো", VIRAMA_STATE: "ও"},
    "act_sign_ou": {"none": "ৌ", VIRAMA_STATE: "ঔ"},
    "act_sign_oi": {"none": "ৈ", VIRAMA_STATE: "ঐ"},
}
ACTION_OUTPUTS = set(ACTION_ID_BY_OUTPUT)

# Non-character keys that should emit control characters in custom layouts.
# Key code 51 (delete/backspace) is intentionally omitted: macOS handles it
# natively, and U+007F is not a legal XML 1.0 character.
SPECIAL_KEYS = (
    {"code": 36, "output": "\r"},
    {"code": 48, "output": "\t"},
    {"code": 49, "output": " "},
)


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
        # Preserve Avro source code points exactly. Bengali letters like ড়/ঢ়/য়
        # are compatibility decomposition exclusions and should not be rewritten.
        mapping[avro_key][state] = value

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
    ET.SubElement(layouts, "layout", {"first": "0", "last": "0", "mapSet": "mapset_0", "modifiers": "modifiers_0"})

    modifier_map = ET.SubElement(keyboard, "modifierMap", {"id": "modifiers_0", "defaultIndex": "0"})
    ET.SubElement(modifier_map, "keyMapSelect", {"mapIndex": "0"})
    ET.SubElement(modifier_map, "keyMapSelect", {"mapIndex": "1"})
    ET.SubElement(modifier_map[0], "modifier", {"keys": ""})
    ET.SubElement(modifier_map[1], "modifier", {"keys": "anyShift"})
    keymap_select_2 = ET.SubElement(modifier_map, "keyMapSelect", {"mapIndex": "2"})
    ET.SubElement(keymap_select_2, "modifier", {"keys": "anyOption"})
    keymap_select_3 = ET.SubElement(modifier_map, "keyMapSelect", {"mapIndex": "3"})
    ET.SubElement(keymap_select_3, "modifier", {"keys": "anyShift anyOption"})
    keymap_select_4 = ET.SubElement(modifier_map, "keyMapSelect", {"mapIndex": "4"})
    ET.SubElement(keymap_select_4, "modifier", {"keys": "anyCommand"})
    keymap_select_5 = ET.SubElement(modifier_map, "keyMapSelect", {"mapIndex": "5"})
    ET.SubElement(keymap_select_5, "modifier", {"keys": "anyShift anyCommand"})
    keymap_select_6 = ET.SubElement(modifier_map, "keyMapSelect", {"mapIndex": "6"})
    ET.SubElement(keymap_select_6, "modifier", {"keys": "anyOption anyCommand"})
    keymap_select_7 = ET.SubElement(modifier_map, "keyMapSelect", {"mapIndex": "7"})
    ET.SubElement(keymap_select_7, "modifier", {"keys": "anyShift anyOption anyCommand"})

    key_map_set = ET.SubElement(keyboard, "keyMapSet", {"id": "mapset_0"})
    sorted_keys = sorted(KEYCODE_BY_AVRO_KEY.items(), key=lambda item: item[1])

    for index, state in enumerate(MODIFIER_ORDER):
        key_map = ET.SubElement(key_map_set, "keyMap", {"index": str(index)})
        for avro_key, keycode in sorted_keys:
            output = mapping.get(avro_key, {}).get(state, "")
            attrs = {"code": str(keycode)}
            if output in ACTION_OUTPUTS:
                attrs["action"] = ACTION_ID_BY_OUTPUT[output]
            else:
                attrs["output"] = output
            ET.SubElement(key_map, "key", attrs)
        for special_key in SPECIAL_KEYS:
            attrs = {k: str(v) for k, v in special_key.items()}
            ET.SubElement(key_map, "key", attrs)

    for index, command_map in ((4, COMMAND_OUTPUT_BY_KEY), (5, SHIFTED_COMMAND_OUTPUT_BY_KEY), (6, COMMAND_OUTPUT_BY_KEY), (7, SHIFTED_COMMAND_OUTPUT_BY_KEY)):
        key_map = ET.SubElement(key_map_set, "keyMap", {"index": str(index)})
        for avro_key, keycode in sorted_keys:
            ET.SubElement(key_map, "key", {"code": str(keycode), "output": command_map[avro_key]})
        for special_key in SPECIAL_KEYS:
            attrs = {k: str(v) for k, v in special_key.items()}
            ET.SubElement(key_map, "key", attrs)

    actions = ET.SubElement(keyboard, "actions")
    for action_id, when_by_state in ACTION_OUTPUT_BY_ID.items():
        action = ET.SubElement(actions, "action", {"id": action_id})
        for state_name, out in when_by_state.items():
            ET.SubElement(action, "when", {"state": state_name, "output": out})

    virama_action = ET.SubElement(actions, "action", {"id": VIRAMA_ACTION_ID})
    ET.SubElement(virama_action, "when", {"state": "none", "next": VIRAMA_STATE})
    ET.SubElement(virama_action, "when", {"state": VIRAMA_STATE, "output": VIRAMA})

    terminators = ET.SubElement(keyboard, "terminators")
    ET.SubElement(terminators, "when", {"state": VIRAMA_STATE, "output": VIRAMA})

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
    parser.add_argument("--keyboard-id", type=int, default=-28676, help="Integer keyboard id")
    parser.add_argument("--group", type=int, default=126, help="Keyboard group id")
    args = parser.parse_args()

    mapping = parse_avro_keydata(args.input)
    xml_text = build_keylayout_xml(mapping, args.layout_name, args.keyboard_id, args.group)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(xml_text, encoding="utf-8")


if __name__ == "__main__":
    main()
