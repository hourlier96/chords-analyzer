from modal_substitution.constants import (
    MODES_DATA,
    NOTES,
    ROMAN_DEGREES,
    CORE_QUALITIES,
    TYPICAL_PATTERNS,
)


# Returns the chromatic index (0–11) for a given note string
def get_note_index(note_str):
    note_map = {
        "DB": "C#",
        "EB": "D#",
        "FB": "E",
        "GB": "F#",
        "AB": "G#",
        "BB": "A#",
        "B#": "C",
    }

    # Normalize the note by stripping extensions and accidentals
    clean_note = (
        note_str.upper()
        .replace("♭", "B")
        .split("M")[0]
        .split("m")[0]
        .split("°")[0]
        .split("dim")[0]
        .split("7")[0]
        .split("ø")[0]
    )

    # Special case for "Cb" (B double flat)
    if clean_note == "CB":
        return 11

    # Map enharmonic equivalents
    if clean_note in note_map:
        clean_note = note_map[clean_note]

    # Return chromatic index
    if len(clean_note) > 1 and clean_note[1] in ["#", "B"]:
        return NOTES.index(clean_note[:2])
    return NOTES.index(clean_note[0])


# Returns note name from chromatic index (0–11)
def get_note_from_index(index):
    return NOTES[index % 12]


# Parses a chord name and returns its root index and a normalized quality string
def parse_chord(chord_name):
    chord_name_c = chord_name.strip()
    root_index = get_note_index(chord_name_c)

    # Match common 7th chord types
    if "maj7" in chord_name_c or "M7" in chord_name_c:
        return root_index, "maj7"
    if "m7b5" in chord_name_c or "ø" in chord_name_c:
        return root_index, "m7b5"
    if "dim7" in chord_name_c or "°7" in chord_name_c:
        return root_index, "dim7"
    if "m7" in chord_name_c:
        return root_index, "m7"
    if "7" in chord_name_c:
        return root_index, "7"
    if "dim" in chord_name_c or "°" in chord_name_c:
        return root_index, "d"
    if "m" in chord_name_c:
        return root_index, "m"
    return root_index, "M"  # Default: major triad


def _format_roman_numeral_from_quality(base_numeral, quality, core_qualities_map):
    """
    Fonction aide : met en forme un chiffrage romain (ex: 'V') et une qualité ('m7')
    en une chaîne de caractères finale (ex: 'v7').
    """
    display_numeral = base_numeral
    core_quality = core_qualities_map.get(quality, "major")  # "major" par défaut
    if core_quality in ["minor", "diminished"]:
        display_numeral = display_numeral.lower()

    suffix_map = {
        "maj7": "maj7",
        "m7": "7",
        "7": "7",
        "m7b5": "ø7",
        "dim7": "°7",
        "dim": "°",
    }
    suffix = suffix_map.get(quality, "")

    return display_numeral + suffix


def get_roman_numeral(chord_name, tonic_index, mode_name):
    """
    Analyse un accord et retourne un tuple contenant le chiffrage attendu (diatonique)
    et le chiffrage réel (joué).
    """
    parsed_chord = parse_chord(chord_name)
    if not parsed_chord:
        return (f"({chord_name})", f"({chord_name})")

    chord_index, found_quality = parsed_chord
    interval = (chord_index - tonic_index + 12) % 12

    mode_intervals, mode_qualities, _ = MODES_DATA[mode_name]

    if interval not in mode_intervals:
        return (f"({chord_name})", f"({chord_name})")

    degree_index = mode_intervals.index(interval)
    base_numeral = ROMAN_DEGREES[degree_index]

    expected_quality = mode_qualities[degree_index]

    expected_numeral = _format_roman_numeral_from_quality(
        base_numeral, expected_quality, CORE_QUALITIES
    )

    found_numeral = _format_roman_numeral_from_quality(
        base_numeral, found_quality, CORE_QUALITIES
    )

    return (expected_numeral, found_numeral)


# Returns a diatonic 7th chord for a degree and tonic, with optional simplification
def get_diatonic_7th_chord(degree, key_tonic_index, mode_name="Ionian"):
    """
    Génère un accord de septième diatonique à partir d'un degré, d'une tonique et d'un mode.
    Cette version est robuste et gère les degrés invalides.
    """
    if degree is None or not (1 <= degree <= 7):
        return None

    mode_intervals, mode_qualities, _ = MODES_DATA[mode_name]

    chord_root_index = (key_tonic_index + mode_intervals[degree - 1]) % 12
    quality = mode_qualities[degree - 1]
    name = get_note_from_index(chord_root_index)

    return name + quality


def is_chord_compatible(found_quality, expected_quality):
    MAJOR_TRIAD_QUALITIES = ["", "maj", "M"]
    MINOR_TRIAD_QUALITIES = ["m", "min"]
    DIMINISHED_TRIAD_QUALITIES = ["dim", "d"]

    if found_quality == expected_quality:
        return True
    if (found_quality in MAJOR_TRIAD_QUALITIES and expected_quality == "maj7") or (
        found_quality == "maj7" and expected_quality in MAJOR_TRIAD_QUALITIES
    ):
        return True
    if (found_quality in MINOR_TRIAD_QUALITIES and expected_quality == "m7") or (
        found_quality == "m7" and expected_quality in MINOR_TRIAD_QUALITIES
    ):
        return True
    if (found_quality in MAJOR_TRIAD_QUALITIES and expected_quality == "7") or (
        found_quality == "7" and expected_quality in MAJOR_TRIAD_QUALITIES
    ):
        return True
    if (found_quality in DIMINISHED_TRIAD_QUALITIES and expected_quality == "m7b5") or (
        found_quality == "m7b5" and expected_quality in DIMINISHED_TRIAD_QUALITIES
    ):
        return True
    if expected_quality in MINOR_TRIAD_QUALITIES and found_quality == "7":
        return True
    return False


def _get_degrees_for_hypothesis(parsed_progression, tonic_idx, mode_intervals):
    try:
        return [
            mode_intervals.index((c[0] - tonic_idx + 12) % 12)
            for c in parsed_progression
        ]
    except ValueError:
        return None


def guess_by_exact_pattern(parsed, modes_data, typical_patterns):
    for tonic_idx in range(12):
        for mode_name, (intervals, qualities, _) in modes_data.items():
            degrees = _get_degrees_for_hypothesis(parsed, tonic_idx, intervals)
            if degrees is None:
                continue

            for pattern in typical_patterns.get(mode_name, []):
                if degrees == pattern["degrees"]:
                    is_fully_compatible = all(
                        is_chord_compatible(parsed[i][1], qualities[degree])
                        for i, degree in enumerate(degrees)
                    )
                    if is_fully_compatible:
                        tonic_note = get_note_from_index(tonic_idx)
                        return [(tonic_note, 100)]
    return None


def guess_by_harmonic_weight(parsed, modes_data):
    tonic_scores = {}
    for tonic_idx in range(12):
        hypotheses = {"Ionian": modes_data["Ionian"], "Aeolian": modes_data["Aeolian"]}
        best_score = -float("inf")

        for mode_name, (intervals, qualities, _) in hypotheses.items():
            score = 0
            for c_idx, c_qual in parsed:
                try:
                    interval = (c_idx - tonic_idx + 12) % 12
                    degree = intervals.index(interval)
                    if not is_chord_compatible(c_qual, qualities[degree]):
                        score -= 2
                        continue

                    if degree == 0:
                        score += 3  # Tonic
                    elif degree == 4:  # Dominant
                        if "m" not in c_qual and "dim" not in c_qual:
                            score += 2
                    elif degree == 3:
                        score += 1  # Sub-dominant
                    else:
                        score += 0.5

                except ValueError:
                    score -= 2

            if score > best_score:
                best_score = score

        tonic_note = get_note_from_index(tonic_idx)
        tonic_scores[tonic_note] = best_score

    return sorted(tonic_scores.items(), key=lambda x: x[1], reverse=True)


def guess_possible_tonics(progression):
    """Fonction principale qui orchestre les deux stratégies."""
    if not progression:
        return []

    parsed = [parse_chord(c) for c in progression]
    if None in parsed:
        return []

    pattern_guess = guess_by_exact_pattern(parsed, MODES_DATA, TYPICAL_PATTERNS)
    if pattern_guess:
        return pattern_guess

    return guess_by_harmonic_weight(parsed, MODES_DATA)


# Formats a list of chord names for display in table columns
def format_chords_for_table(chords, width=7):
    if isinstance(chords, str):
        chords_list = chords.split(" - ")
    else:
        chords_list = chords
    formatted = [f"{chord if chord else '?':<{width}}" for chord in chords_list]
    return " ".join(formatted)
