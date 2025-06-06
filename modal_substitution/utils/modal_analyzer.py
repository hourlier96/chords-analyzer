# -*- coding: utf-8 -*-
from modal_substitution.utils.utils import (
    get_note_index,
    parse_chord,
    is_chord_compatible,
)
from modal_substitution.constants import MODES_DATA


def detect_intelligent_mode(progression, tonic=None):
    """
    Detects the most probable mode of a chord progression.
    Optionally biases detection toward a specific tonic if provided.
    Returns a tuple: (tonic_index, mode_name)
    """
    if not progression:
        return get_note_index("C"), "Ionian"  # Default fallback

    prog_parsed = [parse_chord(c) for c in progression]
    perfect_matches = []

    # Try all combinations of tonic and mode
    for tonic_idx in range(12):
        # Order matters for detection in case of ambiguous progressions
        for mode_name in [
            "Ionian",
            "Aeolian",
            "Dorian",
            "Mixolydian",
            "Lydian",
            "Phrygian",
            "Locrian",
        ]:
            intervals, qualities, _ = MODES_DATA[mode_name]
            is_a_match = True
            chord_degrees = []

            # Compare each chord in the progression with the mode structure
            for c_idx, c_qual in prog_parsed:
                interval = (c_idx - tonic_idx + 12) % 12
                if interval not in intervals:
                    is_a_match = False
                    break
                degree_index = intervals.index(interval)
                expected_quality = qualities[degree_index]
                if not is_chord_compatible(c_qual, expected_quality):
                    is_a_match = False
                    break
                chord_degrees.append(degree_index)

            # If all chords fit the mode, score the match
            if is_a_match:
                score = 0

                # Heuristic scoring criteria
                if chord_degrees and chord_degrees[0] == 0:
                    score += 3  # Starts on I

                for i in range(len(chord_degrees) - 1):
                    if chord_degrees[i] == 4 and chord_degrees[i + 1] == 0:
                        score += 2  # V → I cadence

                if chord_degrees and chord_degrees[-1] == 0:
                    score += 1  # Ends on I

                if 4 in chord_degrees:
                    score += 0.5  # Presence of V

                if prog_parsed[0][0] == tonic_idx:
                    score += 2  # Root match

                if len(chord_degrees) >= 3 and chord_degrees[-3:] == [1, 4, 0]:
                    score += 5  # ii - V - I

                # Special Mixolydian signature: I7 → IVmaj7 → bVIImaj7
                if (
                    len(prog_parsed) >= 3
                    and chord_degrees[:3] == [0, 3, 6]
                    and progression[0].endswith("7")
                    and progression[1].endswith("maj7")
                    and progression[2].endswith("maj7")
                ):
                    score += 5

                if chord_degrees[0] == 0 and progression[0].endswith("7"):
                    score += 2  # Tonic is dominant

                if chord_degrees[:4] == [0, 5, 1, 4]:
                    score += 4  # Anatole

                # Record match
                perfect_matches.append(
                    {"tonic": tonic_idx, "mode": mode_name, "score": score}
                )

    if not perfect_matches:
        return None, None

    # If user specified tonic, prefer it
    if tonic:
        tonic_index = get_note_index(tonic)
        for match in perfect_matches:
            if match["tonic"] == tonic_index:
                return match["tonic"], match["mode"]

    # Return the best-scoring match
    best_match = sorted(perfect_matches, key=lambda m: -m["score"])[0]
    return best_match["tonic"], best_match["mode"]
