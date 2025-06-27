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
        {"degrees": [0, 4, 5, 3]},
        {"degrees": [0, 5, 3, 4]},
        {"degrees": [0, 5, 1, 4]},
        {"degrees": [1, 4, 0]},
        {"degrees": [0, 1, 4, 0]},
        {"degrees": [0, 1, 5, 4]},
        {"degrees": [0, 2, 3, 4]},
        {"degrees": [0, 3, 4, 3]},
        {"degrees": [0, 1, 4, 5]},
        {"degrees": [5, 4, 0]},
        {"degrees": [5, 3, 0, 4]},
        {"degrees": [0, 4, 5, 2, 3, 0, 3, 4]},
    ],
    "Dorian": [
        {"degrees": [0, 3, 4]},
        {"degrees": [0, 6, 3, 4]},
        {"degrees": [0, 1, 2, 3]},
        {"degrees": [0, 2, 3, 6]},
        {"degrees": [0, 4, 0, 3]},
    ],
    "Phrygian": [
        {"degrees": [0, 1, 0, 6]},
        {"degrees": [0, 6, 5, 4]},
        {"degrees": [0, 1, 2, 6]},
    ],
    "Lydian": [
        {"degrees": [0, 1, 5, 2]},
        {"degrees": [0, 1]},
        {"degrees": [0, 2, 1, 4]},
        {"degrees": [0, 1, 4, 0]},
    ],
    "Mixolydian": [
        {"degrees": [0, 6, 3, 4]},
        {"degrees": [0, 3, 4]},
        {"degrees": [0, 6, 0, 3]},
    ],
    "Aeolian": [
        {"degrees": [0, 5, 2, 6]},
        {"degrees": [0, 6, 5, 4]},
        {"degrees": [0, 3, 4, 0]},
        {"degrees": [0, 4, 3, 0]},
        {"degrees": [1, 4, 0]},
        {"degrees": [0, 2, 5, 6]},
        {"degrees": [0, 5, 6, 0]},
    ],
}

RELATIVE_PAIRS = {
    "C": "Am",
    "G": "Em",
    "D": "Bm",
    "A": "F#m",
    "E": "C#m",
    "B": "G#m",
    "F#": "D#m",
    "C#": "A#m",
    "F": "Dm",
    "Bb": "Gm",
    "Eb": "Cm",
    "Ab": "Fm",
}
