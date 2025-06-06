from typing import Dict, List
from harmonic_substitution.constants import FUNCTIONS_BY_KEY


def get_function_for_chord(chord: str, key: str) -> str:
    """Retourne la fonction harmonique d’un accord dans une tonalité donnée."""
    func_map = FUNCTIONS_BY_KEY.get(key, {})
    for func, chords in func_map.items():
        if chord in chords:
            return func
    return "unknown"


def get_functional_substitutions(
    progression: List[str], tonic: str = None
) -> Dict[str, List[str]]:
    """Retourne les substitutions fonctionnelles pour chaque accord d'une progression."""
    if tonic is None:
        tonic = progression[
            0
        ]  # Si aucune tonique n'est donnée, on prend le premier accord
    if tonic not in FUNCTIONS_BY_KEY:
        raise ValueError(
            f"Tonalité '{tonic}' non supportée. Ajoute-la dans FUNCTIONS_BY_KEY."
        )

    func_map = FUNCTIONS_BY_KEY[tonic]
    substitutions = {}

    for chord in progression:
        func = get_function_for_chord(chord, tonic)
        if func in func_map:
            substitutions[chord] = [alt for alt in func_map[func] if alt != chord]
        else:
            substitutions[chord] = []
    return substitutions
