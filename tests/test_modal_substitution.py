import pytest
from modal_substitution.generator import get_substitutions
from modal_substitution.utils.utils import get_note_index


@pytest.mark.parametrize(
    "base_progression, relative_tonic, degrees_to_borrow, expected_result",
    [
        (
            ["C", "Dm", "G", "Am"],
            "C",
            [1, 2, 5, 6],
            ["Cmaj7", "Dm7", "G7", "Am7"],
        ),
        (
            ["C", "Dm", "G", "Am"],
            "A#",
            [1, 2, 5, 6],
            ["A#maj7", "Cm7", "F7", "Gm7"],
        ),
        (
            ["C", "Dm", "G", "Am"],
            "G#",
            [1, 2, 5, 6],
            ["G#maj7", "A#m7", "D#7", "Fm7"],
        ),
        (
            ["C", "Dm", "G", "Am"],
            "G",
            [1, 2, 5, 6],
            ["Gmaj7", "Am7", "D7", "Em7"],
        ),
        (
            ["C", "Dm", "G", "Am"],
            "F",
            [1, 2, 5, 6],
            ["Fmaj7", "Gm7", "C7", "Dm7"],
        ),
        (
            ["C", "Dm", "G", "Am"],
            "D#",
            [1, 2, 5, 6],
            ["D#maj7", "Fm7", "A#7", "Cm7"],
        ),
        (
            ["C", "Dm", "G", "Am"],
            "C#",
            [1, 2, 5, 6],
            ["C#maj7", "D#m7", "G#7", "A#m7"],
        ),
        (
            ["D", "Em", "A", "Bm"],
            "B",
            [1, 2, 5, 6],
            ["Bmaj7", "C#m7", "F#7", "G#m7"],
        ),
    ],
)
def test_get_substitutions_modes(
    base_progression,
    relative_tonic,
    degrees_to_borrow,
    expected_result,
):
    relative_tonic_index = get_note_index(relative_tonic)

    _, new_progression = get_substitutions(
        base_progression,
        relative_tonic_index,
        degrees_to_borrow,
    )

    assert new_progression == expected_result
