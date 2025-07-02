import pytest

from app.utils.common import (
    get_note_index,
    get_note_from_index,
    is_chord_diatonic,
    parse_chord,
    is_dominant_chord,
    get_diatonic_7th_chord,
    _get_core_quality,
)


@pytest.mark.parametrize(
    "note_str, expected_index",
    [
        ("C", 0),
        ("G#", 8),
        ("Ab", 8),  # Enharmonic
        ("B", 11),
        ("B#", 0),  # Enharmonic
        ("Fb", 4),  # Enharmonic (E)
        ("Cb", 11),  # Special case
        ("Fm7", 5),  # With quality
        ("Ddim", 2),  # With quality
    ],
)
def test_get_note_index(note_str, expected_index):
    assert get_note_index(note_str) == expected_index


def test_get_note_index_invalid():
    with pytest.raises(ValueError):
        get_note_index("H")


@pytest.mark.parametrize(
    "index, expected_note", [(0, "C"), (8, "G#"), (11, "B"), (12, "C")]  # Modulo test
)
def test_get_note_from_index(index, expected_note):
    assert get_note_from_index(index) == expected_note


@pytest.mark.parametrize(
    "chord_name, expected_tuple",
    [
        ("Cmaj7", (0, "maj7")),
        ("G#m7", (8, "m7")),
        ("Bbm7b5", (10, "m7b5")),
        ("F#", (6, "")),
        ("Fmaj", (5, "maj")),
        ("D", (2, "")),
        ("Abm", (8, "m")),
        ("Invalid", None),
        ("Hm7", None),
        ("A#", (10, "")),
        ("Cb", (11, "")),
        ("Em", (4, "m")),
        ("Emin", (4, "min")),  # À normaliser vers "m" ou "min"
        ("A7", (9, "7")),
        ("Fdim", (5, "dim")),
        ("123", None),
    ],
)
def test_parse_chord(chord_name, expected_tuple):
    assert parse_chord(chord_name) == expected_tuple


@pytest.mark.parametrize(
    "chord_name, is_dominant",
    [
        ("G7", True),
        ("C9", True),
        ("A", True),
        ("Cmaj7", False),
        ("Am7", False),
        ("Bdim", False),
        ("Gsus4", False),
    ],
)
def test_is_dominant_chord(chord_name, is_dominant):
    assert is_dominant_chord(chord_name) == is_dominant


# 🧪 Tests pour get_diatonic_7th_chord
@pytest.mark.parametrize(
    "degree, key_tonic_index, mode, expected_chord",
    [
        # C Ionian
        (1, 0, "Ionian", "Cmaj7"),
        (2, 0, "Ionian", "Dm7"),
        (5, 0, "Ionian", "G7"),
        (7, 0, "Ionian", "Bm7b5"),
        # D Dorian
        (1, 2, "Dorian", "Dm7"),
        (4, 2, "Dorian", "G7"),
        (7, 2, "Dorian", "Cmaj7"),
        # Invalid degrees
        (0, 0, "Ionian", None),
        (8, 0, "Ionian", None),
    ],
)
def test_get_diatonic_7th_chord(degree, key_tonic_index, mode, expected_chord):
    assert get_diatonic_7th_chord(degree, key_tonic_index, mode) == expected_chord


@pytest.mark.parametrize(
    "quality, expected_core",
    [
        ("maj9", "major"),
        ("m7", "minor"),
        ("m7b5", "diminished"),
        ("°", "diminished"),
        ("aug", "augmented"),
        ("+", "augmented"),
        ("7sus4", "suspended"),
        ("", "major"),
        ("xyz", "major"),  # Fallback
    ],
)
def test_get_core_quality(quality, expected_core):
    assert _get_core_quality(quality) == expected_core


@pytest.mark.parametrize(
    "chord, key, mode, expected",
    [
        # --- Cas en Do Majeur (C Ionian) ---
        # Accords diatoniques exacts (devraient être True)
        ("Cmaj7", "C", "Ionian", True),
        ("G7", "C", "Ionian", True),
        ("Am7", "C", "Ionian", True),
        ("Bm7b5", "C", "Ionian", True),
        # Accords diatoniques simplifiés (triades) (devraient être True)
        ("C", "C", "Ionian", True),
        ("Dm", "C", "Ionian", True),
        ("G", "C", "Ionian", True),
        # Accords suspendus
        ("Gsus2", "C", "Ionian", True),
        ("Csus4", "C", "Ionian", True),
        ("Bsus2", "C", "Ionian", False),
        # Racine diatonique, mais mauvaise qualité (devraient être False)
        ("Gmaj7", "C", "Ionian", False),
        ("A7", "C", "Ionian", False),
        ("Em", "C", "Ionian", True),  # Note: True car 'm' est compatible avec 'm7'
        ("E7", "C", "Ionian", False),
        # Racine non diatonique (devraient être False)
        ("F#m7", "C", "Ionian", False),
        ("Db", "C", "Ionian", False),
        # --- Cas avec une autre tonalité (Ré majeur) ---
        ("Dmaj7", "D", "Ionian", True),
        ("A7", "D", "Ionian", True),
        ("F#m7", "D", "Ionian", True),
        # --- Cas avec un autre mode (La mineur harmonique) ---
        # Note : 'Harmonic Minor' doit être ajouté à MODES_DATA pour que cela fonctionne.
        ("Am(maj7)", "A", "Harmonic Minor", True),  # Degré i
        ("Cmaj7#5", "A", "Harmonic Minor", True),  # Degré III
        ("E7", "A", "Harmonic Minor", True),  # Degré V
        ("Fmaj7", "A", "Harmonic Minor", True),  # Degré VI
        ("G#dim7", "A", "Harmonic Minor", True),  # Degré vii
        ("D7", "A", "Harmonic Minor", False),  # Dm7 est diatonique, pas D7
        # --- Cas invalides ---
        ("InvalidChord", "C", "Ionian", False),
        ("Cmaj7", "X", "Ionian", False),
    ],
)
def test_is_chord_diatonic(chord, key, mode, expected):
    """
    Teste la fonction is_chord_diatonic avec une variété de cas.
    """
    assert is_chord_diatonic(chord, key, mode) == expected
