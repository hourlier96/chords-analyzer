import pytest
from modal_substitution.constants import NOTES
from modal_substitution.utils.modal_analyzer import (
    detect_intelligent_mode,
)

from modal_substitution.utils.utils import get_note_index, get_diatonic_7th_chord


@pytest.mark.parametrize(
    "tonic, mode_name, degrees, expected_chords",
    [
        (
            get_note_index("C"),
            "Ionian",
            [1, 4, 5, 1],
            [
                "Cmaj7",
                "Fmaj7",
                "G7",
                "Cmaj7",
            ],
        ),
        (
            get_note_index("D"),
            "Dorian",
            [1, 4, 7, 1],
            ["Dm7", "G7", "Cmaj7", "Dm7"],
        ),
        (
            get_note_index("G"),
            "Mixolydian",
            [2, 5, 6, 1],
            ["Am7", "Dm7", "Em7", "G7"],
        ),
        (
            get_note_index("A"),
            "Aeolian",
            [1, 2, 3, 7],
            ["Am7", "Bm7b5", "Cmaj7", "G7"],
        ),
    ],
)
def test_01_get_diatonic_7th_chord_expected_chords(
    tonic, mode_name, degrees, expected_chords
):
    chords = [get_diatonic_7th_chord(degree, tonic, mode_name) for degree in degrees]
    assert (
        chords == expected_chords
    ), f"Chords generated {chords} != exx {expected_chords}"


TESTS_CASES = {
    "Ionian": {
        "I-ii-V-I": [1, 2, 5, 1],
        "I-V-vi-IV": [1, 5, 6, 4],
        "I-vi-IV-V": [1, 6, 4, 5],
        "I-vi-ii-V": [1, 6, 2, 5],
        "ii-V-I": [2, 5, 1],
        "I-iii-vi-IV": [1, 3, 6, 4],
        "I-IV-I-V": [1, 4, 1, 5],
        "I-ii-vi-V": [1, 2, 6, 5],
        "I-V-I-IV": [1, 5, 1, 4],
        "I-iii-IV-V": [1, 3, 4, 5],
        "I-IV-V-IV": [1, 4, 5, 4],
        "I-V-vi-iii-IV-I-IV-V": [1, 5, 6, 3, 4, 1, 4, 5],
        "I-vi-iii-IV": [1, 6, 3, 4],
    },
    "Dorian": {
        "i-IV-V": [1, 4, 5],
        "i-ii-VII": [1, 2, 7],
        "i-V-i-IV": [1, 5, 1, 4],
        "i-IV-i-VII": [1, 4, 1, 7],
        "i-IV-i-V": [1, 4, 1, 5],
        "i-ii-IV-i": [1, 2, 4, 1],
        "i-VII-i-V": [1, 7, 1, 5],
        "i-IV-V-VII": [1, 4, 5, 7],
        "i-ii-iii-IV": [1, 2, 3, 4],
        "i-VII-VI-V": [1, 7, 6, 5],
        "i-III-IV-VII": [1, 3, 4, 7],
        "i-IV-VI-V": [1, 4, 6, 5],
    },
    "Phrygian": {
        "i-II-VII-i": [1, 2, 7, 1],
        "i-VII-VI-V": [1, 7, 6, 5],
        "i-v-iv": [1, 5, 4],
        "i-II-i": [1, 2, 1],
        "i-bII-i-bVII": [1, 2, 1, 7],
        "i-iv-ii-i": [1, 4, 2, 1],
        "i-III-VII-i": [1, 3, 7, 1],
        "i-II-III-VII": [1, 2, 3, 7],
        "i-bII-bI-bVII": [1, 2, 1, 7],
        "i-v-i": [1, 5, 1],
        "i-bVII-bVI-bV": [1, 7, 6, 5],
    },
    "Lydian": {
        "I-II-vi-iii": [1, 2, 6, 3],
        "I-II-V-I": [1, 2, 5, 1],
        "I-iii-VII-IV": [1, 3, 7, 4],
        "I-II-IV-I": [1, 2, 4, 1],
        "I-II-IV-V": [1, 2, 4, 5],
        "I-V-VI-II": [1, 5, 6, 2],
        "I-III-II-V": [1, 3, 2, 5],
        "I-II-VI-I": [1, 2, 6, 1],
        "I-IV-ii-V": [1, 4, 2, 5],
        "I-II-III-VI": [1, 2, 3, 6],
        "I-VII-IV-V": [1, 7, 4, 5],
        "I-IV-VI-III": [1, 4, 6, 3],
    },
    "Mixolydian": {
        "I-VII-IV-iii": [1, 7, 4, 3],
        "I-IV-V": [1, 4, 5],
        "I-IV-VII": [1, 4, 7],
        "I-bVII-IV-I": [1, 7, 4, 1],
        "I-IV-I-V": [1, 4, 1, 5],
        "I-VII-V-IV": [1, 7, 5, 4],
        "I-III-IV-V": [1, 3, 4, 5],
        "I-bVII-ii-I": [1, 7, 2, 1],
        "I-bVII-I-IV": [1, 7, 1, 4],
        "I-IV-bVII-bVI": [1, 4, 7, 6],
        "I-bVII-IV-V": [1, 7, 4, 5],
    },
    "Aeolian": {
        "i-VI-III-VII": [1, 6, 3, 7],
        "i-iv-v-i": [1, 4, 5, 1],
        "i-VII-VI-V": [1, 7, 6, 5],
        "i-ii-v": [1, 2, 5],
        "ii-v-i": [2, 5, 1],
        "i-III-VI-VII": [1, 3, 6, 7],
        "i-iv-i-VII": [1, 4, 1, 7],
        "i-v-iv-i": [1, 5, 4, 1],
        "i-ii-iv-v": [1, 2, 4, 5],
        "i-VI-III-iv": [1, 6, 3, 4],
        "i-bVI-bVII-i": [1, 6, 7, 1],
        "i-iv-bVII-VI": [1, 4, 7, 6],
    },
    "Locrian": {
        "i-II-iii": [1, 2, 3],
        "i-v-ii": [1, 5, 2],
        "i-bVII-bV": [1, 7, 5],
        "i-II-i": [1, 2, 1],
        "i-v-ii-i": [1, 5, 2, 1],
        "i-bV-v": [1, 5, 5],
        "i-bVII-ii": [1, 7, 2],
        "i-iii-bV": [1, 3, 5],
        "i-bII-bV": [1, 2, 5],
        "i-bV-bIII": [1, 5, 3],
        "i-bVII-bIII": [1, 7, 3],
    },
}

TESTS_LIST = []
for note in NOTES:
    for mode_name, patterns in TESTS_CASES.items():
        for pattern_name, pattern_degrees in patterns.items():
            test_id = f"{note}-{mode_name}-{pattern_name}"
            TESTS_LIST.append(
                pytest.param(
                    get_note_index(note), mode_name, pattern_degrees, id=test_id
                )
            )


@pytest.mark.parametrize("tonic, mode_name, pattern_degrees", TESTS_LIST)
def test_02_get_mode_from_progression(tonic, mode_name, pattern_degrees):
    expected_mode = mode_name

    progression = [
        get_diatonic_7th_chord(degree, tonic, expected_mode)
        for degree in pattern_degrees
    ]

    _, detected_mode = detect_intelligent_mode(progression)

    progression_str = " -> ".join(progression)

    assert (
        detected_mode == expected_mode
    ), f"For progression '{progression_str}', expected mode was '{expected_mode}', but detected mode is '{detected_mode}'."
