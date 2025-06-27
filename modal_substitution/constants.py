NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
MODES_DATA = {
    "Ionian": (
        [0, 2, 4, 5, 7, 9, 11],
        ["maj7", "m7", "m7", "maj7", "7", "m7", "m7b5"],
        0,
    ),
    "Dorian": (
        [0, 2, 3, 5, 7, 9, 10],
        ["m7", "m7", "maj7", "7", "m7", "m7b5", "maj7"],
        -2,
    ),
    "Phrygian": (
        [0, 1, 3, 5, 7, 8, 10],
        ["m7", "maj7", "7", "m7", "m7b5", "maj7", "m7"],
        -4,
    ),
    "Lydian": (
        [0, 2, 4, 6, 7, 9, 11],
        ["maj7", "7", "m7", "m7b5", "maj7", "m7", "m7"],
        -5,
    ),
    "Mixolydian": (
        [0, 2, 4, 5, 7, 9, 10],
        ["7", "m7", "m7b5", "maj7", "m7", "m7", "maj7"],
        -7,
    ),
    "Aeolian": (
        [0, 2, 3, 5, 7, 8, 10],
        ["m7", "m7b5", "maj7", "m7", "m7", "maj7", "7"],
        -9,
    ),
    "Locrian": (
        [0, 1, 3, 5, 6, 8, 10],
        ["m7b5", "maj7", "m7", "m7", "maj7", "7", "m7"],
        -11,
    ),
}
ROMAN_DEGREES = ["I", "II", "III", "IV", "V", "VI", "VII"]
CORE_QUALITIES = {
    "maj7": "major",
    "M": "major",
    "7": "major",
    "m7": "minor",
    "m": "minor",
    "m7b5": "diminished",
    "dim7": "diminished",
    "d": "diminished",
}

TYPICAL_PATTERNS = {
    "Ionian": [
        {"degrees": [0, 2, 5, 3]},  # I-iii-vi-IV
        {"degrees": [0, 3, 0, 4]},  # I-IV-I-V
    ],
    "Dorian": [
        {"degrees": [0, 3, 0, 6]},  # i-IV-i-VII
        {"degrees": [0, 3, 0, 4]},  # i-IV-i-V
        {"degrees": [0, 3, 4, 6]},  # i-IV-V-VII
        {"degrees": [0, 3, 5, 4]},  # i-IV-VI-V
    ],
    "Phrygian": [
        {"degrees": [0, 3, 1, 0]},  # i-iv-ii-i
        {"degrees": [0, 1, 2, 1]},  # i-ii°-III-I
    ],
    "Lydian": [
        {"degrees": [0, 4, 5, 1]},  # I-V-VI-II
        {"degrees": [0, 3, 1, 4]},  # I-IV-ii-V
        {"degrees": [0, 1, 2, 5]},  # I-II-III-VI
        {"degrees": [0, 3, 5, 2]},  # I-IV-VI-III
    ],
    "Mixolydian": [
        {"degrees": [0, 3, 6]},  # I-IV-VII
        {"degrees": [0, 3, 0, 4]},  # I-IV-I-V
        {"degrees": [0, 3, 6, 5]},  # I-IV-bVII-bVI
        {"degrees": [0, 6, 3, 0]},  # I-bVII-III-I
    ],
    "Aeolian": [
        {"degrees": [0, 1, 4]},  # i-ii-v
        {"degrees": [0, 3, 0, 6]},  # i-iv-i-VII
        {"degrees": [0, 3, 6, 5]},  # i-iv-bVII-VI
    ],
}

CHARACTERISTIC_DEGREES = {
    # La note qui définit le mode par rapport à son équivalent majeur/mineur
    "Lydian": [
        3
    ],  # Le IV# (degré 3, ex: F# pour C Lydien) n'est pas un accord, on vise le II
    "Mixolydian": [6],  # Le bVII (degré 6, ex: Bb pour C Mixolydien)
    "Dorian": [3],  # Le IV majeur (degré 3, ex: F pour C Dorien)
    "Phrygian": [1],  # Le bII majeur (degré 1, ex: Db pour C Phrygien)
}
