import re
from typing import Any, Dict, List, Optional

from app.utils.chords_analyzer import QualityAnalysisItem
from app.utils.common import (
    get_diatonic_7th_chord,
    get_note_from_index,
)
from constants import MAJOR_MODES_DATA, MODES_DATA, ROMAN_DEGREES

TRIAD_QUALITIES = {"", "m", "dim", "aug", "sus2", "sus4"}

SEVENTH_TO_TRIAD_MAP = {
    "maj7": "",
    "maj9": "",
    "maj13": "",
    "maj7#5": "aug",
    "m7": "m",
    "m9": "m",
    "m11": "m",
    "m(maj7)": "m",
    "m6": "m",
    "7": "",  # La triade d'un accord de 7e de dominante est majeure
    "9": "",
    "13": "",
    "7b5": "dim",  # Souvent, la base est diminuée
    "7#5": "aug",
    "m7b5": "dim",
    "dim7": "dim",
    # Ajoutez d'autres correspondances si nécessaire
}


def get_diatonic_triad_chord(degree: int, tonic_index: int, mode_name: str) -> str:
    """
    Construit le nom d'un accord de triade diatonique pour un degré, une tonique et un mode donnés.

    Args:
        degree (int): Le degré de l'accord dans la gamme (1 à 7).
        tonic_index (int): L'index de la note tonique (0-11).
        mode_name (str): Le nom du mode (ex: "Ionian", "Aeolian").

    Returns:
        str: Le nom complet de l'accord de triade (ex: "Dm", "G", "Bdim").
    """
    if mode_name not in MODES_DATA:
        raise ValueError(f"Le mode '{mode_name}' n'est pas reconnu.")
    if not 1 <= degree <= 7:
        raise ValueError("Le degré doit être compris entre 1 et 7.")

    # 1. Obtenir les données du mode
    mode_intervals, mode_seventh_qualities, _ = MODES_DATA[mode_name]

    # 2. Déterminer la fondamentale (root) de l'accord
    # On soustrait 1 au degré car les listes sont indexées à partir de 0
    interval = mode_intervals[degree - 1]
    root_note_index = (tonic_index + interval) % 12
    root_note_name = get_note_from_index(root_note_index)

    # 3. Déterminer la qualité de la triade
    # On récupère d'abord la qualité de 7e diatonique
    seventh_quality = mode_seventh_qualities[degree - 1]
    # Puis on la convertit en sa qualité de triade correspondante
    triad_quality = SEVENTH_TO_TRIAD_MAP.get(seventh_quality, "M")  # "M" par défaut

    # 4. Construire le nom de l'accord final
    # Pour les accords majeurs, la qualité "M" est généralement omise.
    if triad_quality == "M":
        return root_note_name
    else:
        return root_note_name + triad_quality


def get_substitution_info(
    quality_analysis: List[QualityAnalysisItem],
) -> List[Optional[Dict[str, Any]]]:
    """
    ## RENOMMÉE ET MODIFIÉE
    Prend l'analyse et retourne une liste d'informations pour la substitution.

    Pour chaque accord substituable, retourne un dictionnaire avec son degré
    et un booléen `is_triad` indiquant si l'accord original était une triade.
    Retourne `None` pour les accords non substituables.
    """
    substitution_info_list: List[Optional[Dict[str, Any]]] = []

    for analysis_item in quality_analysis:
        found_numeral = analysis_item.get("found_numeral", "")
        found_quality = analysis_item.get("found_quality", "")

        # On ne substitue pas les accords non-diatoniques
        if not found_numeral or found_numeral.startswith("("):
            substitution_info_list.append(None)
            continue

        match = re.match(r"^[ivxIVX]+", found_numeral)
        if match:
            base_numeral_str = match.group(0)
            try:
                degree_num = ROMAN_DEGREES.index(base_numeral_str.upper()) + 1

                ## NOUVEAU : On vérifie si l'accord original est une triade
                is_triad = found_quality in TRIAD_QUALITIES

                substitution_info_list.append({"degree": degree_num, "is_triad": is_triad})
            except ValueError:
                substitution_info_list.append(None)
        else:
            substitution_info_list.append(None)

    return substitution_info_list


def get_substitutions(
    progression: List[str],
    relative_tonic_index: int,
    substitution_info_list: List[Optional[Dict[str, Any]]],
    mode_name: str = "Ionian",
) -> List[dict]:
    """
    Crée une liste d'accords de substitution en se basant sur la nature (triade ou 7e)
    de l'accord original.
    """
    # Qualités des accords de 7e du mode majeur de référence
    major_seventh_qualities = MAJOR_MODES_DATA["Ionian"][1]
    substituted_chords: List[dict] = []

    for index, info in enumerate(substitution_info_list):
        # Cas où l'accord n'est pas substituable
        if info is None:
            substituted_chords.append(
                {
                    "chord": progression[index],
                    "roman": None,
                    "quality": None,
                    "substitution_skipped": True,
                }
            )
            continue

        degree = info["degree"]
        is_original_chord_triad = info["is_triad"]

        # Qualité de 7e diatonique pour ce degré
        seventh_quality = major_seventh_qualities[degree - 1]

        if is_original_chord_triad:
            # Si l'original est une triade, on substitue par une triade
            expected_quality = SEVENTH_TO_TRIAD_MAP.get(seventh_quality, "")
            # On suppose l'existence d'une fonction qui génère la triade diatonique
            chord_name = get_diatonic_triad_chord(degree, relative_tonic_index, mode_name)
        else:
            # Sinon, on substitue par un accord de 7e
            expected_quality = seventh_quality
            chord_name = get_diatonic_7th_chord(degree, relative_tonic_index, mode_name)

        # Formatage du chiffrage romain
        roman_numeral = ROMAN_DEGREES[degree - 1]
        if (
            expected_quality.startswith("m") and not expected_quality.startswith("maj")
        ) or "dim" in expected_quality:
            roman_numeral = roman_numeral.lower()

        substituted_chords.append(
            {
                "chord": chord_name,
                "roman": roman_numeral,
                "quality": expected_quality,
            }
        )

    return substituted_chords
