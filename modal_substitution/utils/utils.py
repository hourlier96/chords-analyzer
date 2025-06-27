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


# Converts a chord name into its Roman numeral in a given mode and tonic
def get_roman_numeral(chord_name, tonic_index, mode_name):
    chord_index, chord_quality = parse_chord(chord_name)
    interval = (chord_index - tonic_index + 12) % 12

    mode_intervals, mode_qualities, _ = MODES_DATA[mode_name]

    if interval in mode_intervals:
        degree_index = mode_intervals.index(interval)
        base_numeral = ROMAN_DEGREES[degree_index]

        # Lowercase for minor or diminished chords
        if CORE_QUALITIES.get(mode_qualities[degree_index]) in ["minor", "diminished"]:
            base_numeral = base_numeral.lower()

        # Add suffix for 7th chords
        quality_map = {
            "maj7": "maj7",
            "m7": "m7",
            "7": "7",
            "m7b5": "ø7",
            "dim7": "°7",
        }
        suffix = quality_map.get(chord_quality, "")
        return base_numeral + suffix

    # If chord doesn't belong to the mode, return it in parentheses
    return f"({chord_name})"


# Returns a diatonic 7th chord for a degree and tonic, with optional simplification
def get_diatonic_7th_chord(degree, key_tonic_index, mode_name="Ionian"):
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


def guess_possible_tonics(progression):
    """
    Devine la ou les toniques les plus probables d'une progression d'accords en utilisant
    un système de scoring hiérarchique pour une stabilité et une précision maximales.
    """
    if not progression:
        return []

    parsed = [parse_chord(c) for c in progression]
    if None in parsed:
        return []

    tonic_scores = {}

    for tonic_idx in range(12):
        # Le score pour chaque hypothèse (tonique, mode) est un tuple.
        # La comparaison se fait élément par élément, dans l'ordre de priorité.
        # (matches, strong_cadence, anchor, cadence, dominant, pattern)
        best_score_tuple = (-1, -1, -1, -1, -1, -1)

        for mode_name, (intervals, qualities, _) in MODES_DATA.items():

            # --- Étape 1: Calcul des degrés et de la compatibilité diatonique ---
            chord_degrees = []
            compatible_chords_count = 0

            for i in range(len(parsed)):
                c_idx, c_qual = parsed[i]
                try:
                    interval = (c_idx - tonic_idx + 12) % 12
                    degree = intervals.index(interval)
                    chord_degrees.append(degree)

                    if is_chord_compatible(c_qual, qualities[degree]):
                        compatible_chords_count += 1
                except ValueError:
                    chord_degrees.append(None)

            # --- Étape 2: Calcul des scores pour la hiérarchie de décision ---

            # Critère 1: Nombre de correspondances (le plus important)
            score_matches = compatible_chords_count

            prog_degrees_list = [d for d in chord_degrees if d is not None]

            # Critère 2: Présence de la cadence "parfaite" ii-V-I (bris d'égalité très fort)
            is_ii_v_i = prog_degrees_list == [1, 4, 0]
            score_strong_cadence = 1 if is_ii_v_i else 0

            # Critère 3: Ancrage sur la tonique (commence par I)
            score_anchor = 1 if chord_degrees and chord_degrees[0] == 0 else 0

            # Critère 4: Présence d'une cadence V-I générique
            prog_degrees_str = " ".join(map(str, prog_degrees_list))
            score_cadence = 1 if "4 0" in prog_degrees_str else 0

            # Critère 5: Présence d'une dominante fonctionnelle
            score_dominant = 0
            for i, degree in enumerate(chord_degrees):
                if degree == 4:
                    _, chord_quality = parsed[i]
                    if "m" not in chord_quality and "dim" not in chord_quality:
                        score_dominant = 1
                        break

            # Critère 6: La progression est un motif connu (bris d'égalité final)
            score_pattern = 0
            for pattern in TYPICAL_PATTERNS.get(mode_name, []):
                if prog_degrees_list == pattern["degrees"]:
                    score_pattern = 1
                    break

            # --- Étape 3: Création du tuple de score hiérarchique ---
            current_score_tuple = (
                score_matches,
                score_strong_cadence,
                score_anchor,
                score_cadence,
                score_dominant,
                score_pattern,
            )

            # Python compare les tuples nativement, élément par élément
            if current_score_tuple > best_score_tuple:
                best_score_tuple = current_score_tuple

        tonic_note = get_note_from_index(tonic_idx)
        tonic_scores[tonic_note] = best_score_tuple

    # Tri final basé sur la comparaison des tuples de score
    return sorted(tonic_scores.items(), key=lambda x: x[1], reverse=True)


# Formats a list of chord names for display in table columns
def format_chords_for_table(chords, width=7):
    if isinstance(chords, str):
        chords_list = chords.split(" - ")
    else:
        chords_list = chords
    formatted = [f"{chord:<{width}}" for chord in chords_list]
    return " ".join(formatted)
