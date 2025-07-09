import re
from typing import List, Optional

from app.utils.chords_analyzer import QualityAnalysisItem
from app.utils.common import (
    get_diatonic_7th_chord,
)
from constants import MAJOR_MODES_DATA, ROMAN_DEGREES


def get_degrees_to_borrow(quality_analysis: List[QualityAnalysisItem]) -> List[Optional[int]]:
    """
    Prend le résultat de l'analyse détaillée et retourne une liste de degrés numériques (1-7)
    pour les accords qui sont des candidats à la substitution.

    Les accords de tonique (I) et les accords non-diatoniques ne sont pas substituables
    et seront représentés par `None`.
    """
    degrees_to_borrow: List[Optional[int]] = []

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
    progression: List[str],
    relative_tonic_index: int,
    degrees_to_borrow: List[Optional[int]],
    mode_name: str = "Ionian",
) -> List[dict]:
    """
    Crée une liste d'accords de substitution à partir d'une liste de degrés, en les
    enrichissant avec le chiffrage et la qualité de la gamme majeure relative du mode fournit.

    Pour mode_name="Phrygian" : La variable relative_tonic_index pointera correctement vers G#.
    Il construira donc les accords de la gamme de G# Majeur.

    Args:
        quality_analysis (list): L'analyse détaillée de la progression d'accords.
        relative_tonic_index (int): L'index de la note tonique pour la substitution.
        degrees_to_borrow (list): Une liste de degrés (1-7) ou `None`.

    Returns:
        list: Une liste de dictionnaires, chaque dictionnaire représentant un accord
              substitué avec son nom, son degré, son chiffrage romain et sa qualité.
    """
    mode_qualities = MAJOR_MODES_DATA["Ionian"][1]
    borrowed_chords: List[dict] = []

    for degree_index in degrees_to_borrow:
        if degree_index is None:
            borrowed_chords.append(
                {
                    "chord": "N/A",
                    "roman": None,
                    "quality": None,
                }
            )
            continue

        roman_numeral = ROMAN_DEGREES[degree_index - 1]
        quality = mode_qualities[degree_index - 1]
        if (quality.startswith("m") and not quality.startswith("maj")) or "dim" in quality:
            roman_numeral = roman_numeral.lower()

        borrowed_chords.append(
            {
                "chord": get_diatonic_7th_chord(degree_index, relative_tonic_index, mode_name),
                "roman": roman_numeral,
                "quality": quality,
            }
        )

    new_progression_chords: List[dict] = []
    if not borrowed_chords:
        return [{"chord": chord, "roman": None, "quality": None} for chord in progression]

    borrowed_idx = 0
    for _ in progression:
        new_progression_chords.append(borrowed_chords[borrowed_idx % len(borrowed_chords)])
        borrowed_idx += 1

    return new_progression_chords
