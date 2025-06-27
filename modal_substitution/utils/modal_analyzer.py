from modal_substitution.utils.utils import (
    get_note_index,
    parse_chord,
    is_chord_compatible,
)
from modal_substitution.constants import CORE_QUALITIES, MODES_DATA, TYPICAL_PATTERNS


def detect_mode(progression, tonic):
    """
    Détecte le mode le plus probable en utilisant un scoring hiérarchique
    qui intègre les motifs comme bris d'égalité final.
    """
    tonic_idx = get_note_index(tonic)
    if tonic_idx is None or not progression:
        return None

    parsed = [parse_chord(c) for c in progression]
    if None in parsed:
        return None

    best_mode_name = None
    best_score_tuple = (-1, -1, -1, -1, -1)

    for mode_name, (intervals, qualities, _) in MODES_DATA.items():

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

        # --- Calcul des scores pour la hiérarchie ---
        # Critère 1: Nombre de correspondances
        score_matches = compatible_chords_count

        # Critère 2: Bonus d'ancrage (commence sur la tonique)
        score_anchor = 1 if chord_degrees and chord_degrees[0] == 0 else 0

        # Critère 3: Bonus de cadence V-I
        prog_degrees_str = " ".join(
            map(str, [d for d in chord_degrees if d is not None])
        )
        score_cadence = 1 if "4 0" in prog_degrees_str else 0

        # Critère 4: Bonus de dominante fonctionnelle
        score_dominant = 0
        for i, degree in enumerate(chord_degrees):
            if degree == 4:
                _, chord_quality = parsed[i]
                # Utilise votre fonction CORE_QUALITIES pour être plus robuste
                if CORE_QUALITIES.get(chord_quality) == "major":
                    score_dominant = 1
                    break

        # Critère 5: Bonus de motif (bris d'égalité final)
        score_pattern = 0
        prog_degrees_list = [d for d in chord_degrees if d is not None]
        for pattern in TYPICAL_PATTERNS.get(mode_name, []):
            if prog_degrees_list == pattern["degrees"]:
                score_pattern = 1
                break

        # Création du tuple de score final
        current_score_tuple = (
            score_matches,
            score_anchor,
            score_cadence,
            score_dominant,
            score_pattern,
        )

        if current_score_tuple > best_score_tuple:
            best_score_tuple = current_score_tuple
            best_mode_name = mode_name

    return best_mode_name
