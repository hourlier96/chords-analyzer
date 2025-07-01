NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

ROMAN_DEGREES = ["I", "II", "III", "IV", "V", "VI", "VII"]
CORE_QUALITIES = {
    # Majeurs
    "": "major",
    "M": "major",
    "maj": "major",
    "maj7": "major",
    "maj9": "major",
    "maj7#5": "major",
    # Mineurs
    "m": "minor",
    "min": "minor",
    "m7": "minor",
    "m6": "minor",
    "m9": "minor",
    "m11": "minor",
    "m(maj7)": "minor",
    # Dominantes
    "7": "dominant",
    "7b5": "dominant",
    "7#5": "dominant",
    "7b9": "dominant",
    "7#9": "dominant",
    "13": "dominant",
    # Diminués
    "dim": "diminished",
    "d": "diminished",
    "dim7": "diminished",
    "m7b5": "diminished",
    # Augmentés
    "aug": "augmented",
    # Suspendus
    "sus2": "suspended",
    "sus4": "suspended",
}

CHARACTERISTIC_DEGREES = {
    "Lydian": [3],
    "Mixolydian": [6],
    "Dorian": [3],
    "Phrygian": [1],
}

MODES_DATA = {}
MAJOR_MODES_DATA = {
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

# --- Modes de la gamme mineure harmonique ---
HARMONIC_MINOR_MODES = {
    "Harmonic Minor": (
        [0, 2, 3, 5, 7, 8, 11],
        ["m(maj7)", "m7b5", "maj7#5", "m7", "7", "maj7", "dim7"],
        None,
    ),
    "Locrian ♮6": (
        [0, 1, 3, 5, 6, 9, 10],
        ["m7b5", "maj7#5", "m7", "7", "maj7", "dim7", "m(maj7)"],
        None,
    ),
    "Ionian #5": (
        [0, 2, 4, 5, 8, 9, 11],
        ["maj7#5", "m7", "7", "maj7", "dim7", "m(maj7)", "m7b5"],
        None,
    ),
    "Dorian #4": (
        [0, 2, 3, 6, 7, 9, 10],
        ["m7", "7", "maj7", "dim7", "m(maj7)", "m7b5", "maj7#5"],
        None,
    ),
    "Phrygian Dominant": (
        [0, 1, 4, 5, 7, 8, 10],
        ["7", "maj7", "dim7", "m(maj7)", "m7b5", "maj7#5", "m7"],
        None,
    ),
    "Lydian #2": (
        [0, 3, 4, 6, 7, 9, 11],
        ["maj7", "dim7", "m(maj7)", "m7b5", "maj7#5", "m7", "7"],
        None,
    ),
    "Super Locrian bb7": (
        [0, 1, 3, 4, 6, 8, 9],
        ["dim7", "m(maj7)", "m7b5", "maj7#5", "m7", "7", "maj7"],
        None,
    ),
}

# --- Modes de la gamme mineure mélodique ---
MELODIC_MINOR_MODES = {
    "Melodic Minor": (
        [0, 2, 3, 5, 7, 9, 11],
        ["m(maj7)", "m7", "maj7#5", "7", "7", "m7b5", "m7b5"],
        None,
    ),
    "Dorian b2": (
        [0, 1, 3, 5, 7, 9, 10],
        ["m7", "maj7#5", "7", "7", "m7b5", "m7b5", "m(maj7)"],
        None,
    ),
    "Lydian #5": (
        [0, 2, 4, 6, 8, 9, 11],
        ["maj7#5", "7", "7", "m7b5", "m7b5", "m(maj7)", "m7"],
        None,
    ),
    "Lydian Dominant": (
        [0, 2, 4, 6, 7, 9, 10],
        ["7", "7", "m7b5", "m7b5", "m(maj7)", "m7", "maj7#5"],
        None,
    ),
    "Mixolydian b6": (
        [0, 2, 4, 5, 7, 8, 10],
        ["7", "m7b5", "m7b5", "m(maj7)", "m7", "maj7#5", "7"],
        None,
    ),
    "Locrian ♮2": (
        [0, 2, 3, 5, 6, 8, 10],
        ["m7b5", "m7b5", "m(maj7)", "m7", "maj7#5", "7", "7"],
        None,
    ),
    "Altered Scale": (
        [0, 1, 3, 4, 6, 8, 10],
        ["m7b5", "m(maj7)", "m7", "maj7#5", "7", "7", "m7b5"],
        None,
    ),
}

MODES_DATA.update(MAJOR_MODES_DATA)
MODES_DATA.update(HARMONIC_MINOR_MODES)
MODES_DATA.update(MELODIC_MINOR_MODES)


# Only used by manual mode detection
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
