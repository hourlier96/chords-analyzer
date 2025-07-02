from app.utils.common import (
    get_note_from_index,
    is_chord_diatonic,
    parse_chord,
)
from constants import CORE_QUALITIES, MODES_DATA, ROMAN_DEGREES


def analyze_chord_in_context(chord_name, tonic_index, mode_name):
    """
    Analyse un accord dans un contexte tonal/modal et retourne un dictionnaire
    détaillé contenant toutes les informations d'analyse.
    """

    def _format_numeral(base_numeral, quality):
        core_quality = CORE_QUALITIES.get(quality, "major")
        numeral = (
            base_numeral.lower()
            if core_quality in ["minor", "diminished"]
            else base_numeral
        )

        suffix_map = {
            # Majeurs
            "maj7": "maj7",
            "maj7#5": "maj7#5",
            "maj9": "maj9",
            # Mineurs
            "m7": "7",
            "m(maj7)": "maj7",
            "m6": "6",
            "m9": "9",
            "m11": "11",
            # Dominants
            "7": "7",
            "7b5": "7♭5",
            "7#5": "7♯5",
            "7b9": "7♭9",
            "7#9": "7♯9",
            "13": "13",
            # Diminués
            "m7b5": "ø7",
            "dim": "°",
            "dim7": "°7",
            # Augmentés
            "aug": "+",
            # Suspendus
            "sus2": "sus2",
            "sus4": "sus4",
        }

        suffix = suffix_map.get(quality, "")
        return numeral + suffix

    # --- Analyse principale ---
    parsed_chord = parse_chord(chord_name)
    if not parsed_chord:
        return {"chord": chord_name, "error": "Invalid Chord"}

    chord_index, found_quality = parsed_chord
    interval = (chord_index - tonic_index + 12) % 12

    mode_intervals, mode_qualities, _ = MODES_DATA[mode_name]

    if interval not in mode_intervals:
        return {
            "chord": chord_name,
            "found_numeral": f"({chord_name})",
            "expected_numeral": "N/A",
            "found_quality": found_quality,
            "expected_quality": None,
            "is_diatonic": False,
        }

    degree_index = mode_intervals.index(interval)
    base_numeral = ROMAN_DEGREES[degree_index]
    expected_quality = mode_qualities[degree_index]

    expected_root_index = (tonic_index + mode_intervals[degree_index]) % 12
    expected_root_name = get_note_from_index(expected_root_index)
    expected_chord_name = expected_root_name + expected_quality

    expected_numeral = _format_numeral(base_numeral, expected_quality)
    found_numeral = _format_numeral(base_numeral, found_quality)

    return {
        "chord": chord_name,
        "found_numeral": found_numeral,
        "expected_numeral": expected_numeral,
        "found_quality": found_quality,
        "expected_quality": expected_quality,
        "expected_chord_name": expected_chord_name,
        "is_diatonic": is_chord_diatonic(
            chord_name, get_note_from_index(tonic_index), mode_name
        ),
    }
