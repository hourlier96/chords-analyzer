from app.utils.common import (
    get_note_from_index,
    is_chord_diatonic,
    parse_chord,
)
from constants import CORE_QUALITIES, MODES_DATA, ROMAN_DEGREES

CHROMATIC_DEGREES_MAP = {
    0: "I",
    1: "bII",
    2: "II",
    3: "bIII",
    4: "III",
    5: "IV",
    6: "#IV",
    7: "V",
    8: "bVI",
    9: "VI",
    10: "bVII",
    11: "VII",
}

# Defines the parallel mode for borrowing chords
PARALLEL_MODES = {
    "Ionian": "Aeolian",
    "Dorian": "Phrygian",  # Exemple, à adapter si besoin
    "Phrygian": "Dorian",  # Exemple
    "Lydian": "Mixolydian",  # Exemple
    "Mixolydian": "Lydian",  # Exemple
    "Aeolian": "Ionian",
}


def analyze_chord_in_context(chord_name, tonic_index, mode_name):
    """
    Analyse un accord dans un contexte tonal/modal, en gérant les accords
    diatoniques et les emprunts courants.
    """

    def _format_numeral(base_numeral, quality):
        core_quality = CORE_QUALITIES.get(quality, "major")
        numeral = (
            base_numeral.lower()
            if core_quality in ["minor", "diminished"]
            else base_numeral
        )
        suffix_map = {
            "maj7": "maj7",
            "maj7#5": "maj7#5",
            "maj9": "maj9",
            "m7": "7",
            "m(maj7)": "maj7",
            "m6": "6",
            "m9": "9",
            "m11": "11",
            "7": "7",
            "7b5": "7♭5",
            "7#5": "7♯5",
            "7b9": "7♭9",
            "7#9": "7♯9",
            "13": "13",
            "m7b5": "ø7",
            "dim": "°",
            "dim7": "°7",
            "aug": "+",
            "sus2": "sus2",
            "sus4": "sus4",
            "add9": "add9",
        }
        suffix = suffix_map.get(quality, "")
        if not suffix and quality and quality not in ["", "M"]:
            if quality.startswith("add"):
                suffix = quality
        return numeral + suffix

    # --- Analyse principale ---
    parsed_chord = parse_chord(chord_name)
    if not parsed_chord:
        return {"chord": chord_name, "error": "Invalid Chord"}

    chord_index, found_quality = parsed_chord
    interval = (chord_index - tonic_index + 12) % 12

    base_numeral = CHROMATIC_DEGREES_MAP.get(interval)
    if not base_numeral:
        return {"chord": chord_name, "error": "Invalid Interval"}

    found_numeral = _format_numeral(base_numeral, found_quality)

    is_diatonic_flag = is_chord_diatonic(
        chord_name, get_note_from_index(tonic_index), mode_name
    )

    # --- Logique pour déterminer l'accord "attendu" ---
    expected_quality = None
    expected_numeral = "N/A"
    expected_chord_name = "N/A"

    mode_intervals, mode_qualities, _ = MODES_DATA[mode_name]

    # Cas 1: L'accord est diatonique. L'attente est l'accord lui-même.
    if is_diatonic_flag:
        degree_index = mode_intervals.index(interval)
        expected_quality = mode_qualities[degree_index]
        diatonic_base_numeral = ROMAN_DEGREES[degree_index]
        expected_numeral = _format_numeral(diatonic_base_numeral, expected_quality)

    # Cas 2: L'accord n'est pas diatonique.
    else:
        # Sous-cas 2a: La fondamentale est diatonique, mais la qualité est altérée.
        if interval in mode_intervals:
            # L'attente par défaut est l'accord diatonique du mode ACTUEL.
            degree_index = mode_intervals.index(interval)
            expected_quality = mode_qualities[degree_index]
            diatonic_base_numeral = ROMAN_DEGREES[degree_index]
            expected_numeral = _format_numeral(diatonic_base_numeral, expected_quality)

            # *** DÉBUT DE LA CORRECTION DU BUG ***
            # EXCEPTION: Le V7 en mode mineur est si courant qu'il est considéré comme l'attente par défaut.
            if mode_name == "Aeolian" and base_numeral == "V" and found_quality == "7":
                parallel_mode_name = PARALLEL_MODES.get(mode_name)  # 'ionian'
                if parallel_mode_name:
                    p_intervals, p_qualities, _ = MODES_DATA[parallel_mode_name]
                    if interval in p_intervals:
                        p_degree_index = p_intervals.index(interval)
                        # On prend la qualité attendue ('7') du mode majeur parallèle.
                        expected_quality = p_qualities[p_degree_index]
                        expected_numeral = _format_numeral(
                            base_numeral, expected_quality
                        )
            # *** FIN DE LA CORRECTION DU BUG ***

        # Sous-cas 2b: La fondamentale est chromatique. L'attente vient du mode parallèle.
        else:
            parallel_mode_name = PARALLEL_MODES.get(mode_name)
            if parallel_mode_name:
                p_intervals, p_qualities, _ = MODES_DATA[parallel_mode_name]
                if interval in p_intervals:
                    degree_index = p_intervals.index(interval)
                    expected_quality = p_qualities[degree_index]
                    expected_numeral = _format_numeral(base_numeral, expected_quality)

    # Calcul du nom de l'accord attendu si une qualité a été trouvée
    if expected_quality is not None:
        expected_root_index = (tonic_index + interval) % 12
        expected_root_name = get_note_from_index(expected_root_index)

        if "b" in base_numeral and "#" in expected_root_name:
            flat_note_index = (expected_root_index + 1) % 12
            expected_root_name = get_note_from_index(flat_note_index) + "b"

        expected_chord_name = expected_root_name + expected_quality

    return {
        "chord": chord_name,
        "found_numeral": found_numeral,
        "expected_numeral": expected_numeral,
        "found_quality": found_quality,
        "expected_quality": expected_quality,
        "expected_chord_name": expected_chord_name,
        "is_diatonic": is_diatonic_flag,
    }
