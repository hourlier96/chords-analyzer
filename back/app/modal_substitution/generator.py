import re
from app.utils.common import (
    get_diatonic_7th_chord,
)
from constants import ROMAN_DEGREES


def get_degrees_to_borrow(quality_analysis: list[dict]) -> list[int | None]:
    """
    Prend le résultat de l'analyse détaillée et retourne une liste de degrés numériques (1-7)
    pour les accords qui sont des candidats à la substitution.

    Les accords de tonique (I) et les accords non-diatoniques ne sont pas substituables
    et seront représentés par `None`.
    """
    degrees_to_borrow = []

    for analysis_item in quality_analysis:
        found_numeral = analysis_item.get("found_numeral", "")

        # Cas 2 : L'accord n'est pas diatonique (ex: "(G7)"). On ne le substitue pas.
        if not found_numeral or found_numeral.startswith("("):
            degrees_to_borrow.append(None)
            continue

        # Cas 3 : C'est un accord diatonique non-tonique. On extrait son degré.
        match = re.match(r"^[ivxIVX]+", found_numeral)
        if match:
            base_numeral_str = match.group(0)
            try:
                # On trouve l'index (0-6) et on ajoute 1 pour obtenir le degré (1-7)
                degree_num = ROMAN_DEGREES.index(base_numeral_str.upper()) + 1
                degrees_to_borrow.append(degree_num)
            except ValueError:
                # Sécurité si le chiffrage est inattendu
                degrees_to_borrow.append(None)
        else:
            degrees_to_borrow.append(None)

    return degrees_to_borrow


def get_substitutions(
    base_progression,
    relative_tonic_index,
    degrees_to_borrow,
):
    # Get the equivalent chords from the new mode
    borrowed_chords = [
        get_diatonic_7th_chord(
            deg,
            relative_tonic_index,
        )
        for i, deg in enumerate(degrees_to_borrow)
    ]

    # Reconstruct the full progression with substitutions
    new_progression_chords = []
    borrowed_idx = 0
    for _ in base_progression:
        new_progression_chords.append(borrowed_chords[borrowed_idx])
        borrowed_idx += 1

    return new_progression_chords
