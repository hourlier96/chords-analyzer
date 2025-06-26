from modal_substitution.utils.utils import (
    get_note_index,
    parse_chord,
    is_chord_compatible,
)
from modal_substitution.constants import MODES_DATA, TYPICAL_PATTERNS


def detect_mode(progression, tonic):
    tonic_idx = get_note_index(tonic)
    if tonic_idx is None:
        return None
    prog_parsed = [parse_chord(c) for c in progression]
    if None in prog_parsed:
        return None

    best_mode = None
    best_score = -float("inf")

    for mode_name, (intervals, qualities, _) in MODES_DATA.items():
        chord_degrees = []
        compatibility_mask = []

        for c_idx, c_qual in prog_parsed:
            try:
                interval = (c_idx - tonic_idx + 12) % 12
                degree = intervals.index(interval)
                chord_degrees.append(degree)

                expected_quality = qualities[degree]
                is_compatible = is_chord_compatible(c_qual, expected_quality)
                compatibility_mask.append(is_compatible)
            except ValueError:
                chord_degrees.append(None)
                compatibility_mask.append(False)

        match_count = sum(compatibility_mask)
        if match_count < len(progression) / 2:
            continue
        penalty_count = len(progression) - match_count
        score = match_count - (penalty_count * 0.5)

        if chord_degrees and chord_degrees[0] == 0:
            score += 5

        total_pattern_score = 0
        prog_str = " ".join(map(str, [d for d in chord_degrees if d is not None]))

        sorted_patterns = sorted(
            TYPICAL_PATTERNS.get(mode_name, []),
            key=lambda p: len(p["degrees"]),
            reverse=True,
        )

        for pattern in sorted_patterns:
            pattern_str = " ".join(map(str, pattern["degrees"]))

            try:
                start_index = prog_str.find(pattern_str)
                if start_index != -1:
                    is_pattern_fully_compatible = all(
                        compatibility_mask[i]
                        for i in range(
                            start_index, start_index + len(pattern["degrees"])
                        )
                    )

                    if is_pattern_fully_compatible:
                        total_pattern_score += pattern["score"]
                    else:
                        total_pattern_score += pattern["score"] * 0.25

                    prog_str = prog_str.replace(pattern_str, "", 1)
            except Exception:
                continue

        score += total_pattern_score

        if score > best_score:
            best_score = score
            best_mode = mode_name

    return best_mode
