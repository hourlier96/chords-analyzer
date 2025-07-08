import os
import google.generativeai as genai

from constants import MODES_DATA


def detect_tonic_and_mode(progression: list[str], model) -> tuple[str, str, str]:
    """
    Détermine la tonique, le mode et les explications d'une progression
    en utilisant l'API Google Gemini pour une analyse plus fiable et performante.
    """

    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    except Exception:
        raise ValueError(
            "Clé API Gemini non trouvée. Veuillez la définir dans vos variables d'environnement."
        )

    # --- Initialisation du modèle ---
    model = genai.GenerativeModel(model)

    # --- Création du prompt ---
    # Le prompt est modifié pour demander des explications détaillées avant la tonique et le mode.
    prompt = (
        "# Rôle et Objectif"
        "Identifie la tonalité (tonique et mode) la plus probable d'une progression d'accords donnée."
        " "
        "# Instructions et Contraintes Strictes"
        "   **Explication :** Fournis une explication brève et technique (1 à 2 phrases maximum) justifiant ton choix. Mentionne les degrés clés (ex: I, V, IV) ou les mouvements cadentiels qui confirment la tonalité."
        "   **Format de Sortie :** La dernière ligne de ta réponse doit **impérativement et uniquement** contenir la tonalité finale, formatée comme suit : `TONIQUE MODE`."
        "   **Nomenclature de la Tonique :** La tonique doit toujours être représentée par sa notation lettrée (A, B, C, D, E, F, G), incluant les altérations si nécessaire (ex: Bb, F#)."
        f"  **Modes Valides :** Le mode doit **obligatoirement** appartenir à la liste suivante (la casse est très importante): {MODES_DATA.keys()}."
        " "
        "---"
        f"Progression à analyser : {' - '.join(progression)}"
    )

    try:
        # --- Appel à l'API ---
        response = model.generate_content(prompt)

        # --- Traitement de la réponse ---
        content = response.text.strip()

        # On cherche la dernière ligne qui contient la tonique et le mode
        lines = content.split("\n")
        if not lines:
            raise ValueError(f"Réponse de l'API vide ou mal formatée : '{content}'")

        # La dernière ligne doit être la tonique et le mode
        last_line = lines[-1].strip()

        if " " in last_line:
            parts = last_line.split(" ", 1)
            tonic = parts[0].strip()
            mode = parts[1].strip()

            # L'explication sera toutes les lignes sauf la dernière
            explanation = "\n".join(lines[:-1]).strip()
            return tonic, mode, explanation
        else:
            raise ValueError(
                f"La dernière ligne de l'API est mal formatée pour la tonique et le mode : '{last_line}'"
            )

    except Exception as e:
        # Gère les erreurs potentielles de l'API (ex: clé invalide, problème de connexion)
        print(f"Une erreur est survenue lors de l'appel à l'API Gemini : {e}")
        raise
