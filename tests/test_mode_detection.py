import pytest
from constants import TYPICAL_PATTERNS

from utils.common import (
    get_note_index,
    get_diatonic_7th_chord,
)
from utils.mode_detection import detect_mode, guess_possible_tonics


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


TONIC_TESTS = []
for mode_name, patterns_list in TYPICAL_PATTERNS.items():
    for pattern_info in patterns_list:
        degrees_base0 = pattern_info["degrees"]

        pattern_name = "-".join([str(d + 1) for d in degrees_base0])

        tonic_index = get_note_index("C")

        progression = [
            get_diatonic_7th_chord(degree + 1, tonic_index, mode_name)
            for degree in degrees_base0
        ]

        if None in progression:
            continue

        test_id = f"C-{mode_name}-{pattern_name}"

        TONIC_TESTS.append(pytest.param("C", progression, id=test_id))


@pytest.mark.parametrize("expected_tonic, progression", TONIC_TESTS)
def test_02_tonic_detection(expected_tonic, progression):
    tonic_candidates = guess_possible_tonics(progression)
    detected_tonic, _ = tonic_candidates[0]
    progression_str = " -> ".join(progression)

    assert detected_tonic == expected_tonic, (
        f"For progression '{progression_str}', expected tonic was '{expected_tonic}', "
        f"but detected tonic is '{detected_tonic}'."
    )


TESTS_LIST = []
for mode_name, patterns_list in TYPICAL_PATTERNS.items():
    for pattern_info in patterns_list:
        degrees_base0 = pattern_info["degrees"]

        pattern_name = "-".join([str(d + 1) for d in degrees_base0])

        tonic_note = "C"
        tonic_index = get_note_index(tonic_note)

        test_id = f"{tonic_note}-{mode_name}-{pattern_name}"

        degrees_base1 = [d + 1 for d in degrees_base0]

        TESTS_LIST.append(
            pytest.param(tonic_index, mode_name, degrees_base1, id=test_id)
        )


@pytest.mark.parametrize("tonic, mode_name, pattern_degrees", TESTS_LIST)
def test_03_get_mode(tonic, mode_name, pattern_degrees):
    expected_mode = mode_name

    progression = [
        get_diatonic_7th_chord(degree, tonic, expected_mode)
        for degree in pattern_degrees
    ]

    tonic_guess = guess_possible_tonics(progression)
    assert (
        tonic_guess
    ), f"No tonic could be guessed from progression: {' -> '.join(progression)}"
    guessed_tonic = tonic_guess[0][0]

    detected_mode = detect_mode(progression, guessed_tonic)

    progression_str = " -> ".join(progression)

    assert (
        detected_mode == expected_mode
    ), f"For progression '{progression_str}', expected mode was '{expected_mode}', but detected mode is '{detected_mode}'."
