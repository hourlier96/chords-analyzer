import os
import google.generativeai as genai

from constants import MODES_DATA


def detect_tonic_and_mode(progression: list[str]) -> tuple[str, str, str]:
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
    model = genai.GenerativeModel("gemini-2.5-flash")

    # --- Création du prompt ---
    # Le prompt est modifié pour demander des explications détaillées avant la tonique et le mode.
    prompt = (
        "Tu es un expert en théorie musicale. Ton rôle est d'analyser une progression d'accords et de déterminer sa tonalité la plus probable (tonique et mode).\n"
        "Si tu dois choisir parmi plusieurs possibilités, retiens celle qui contient le moins d'accords d'emprunts."
        "L'explication doit être la plus concise possible, assez courte. Termine ta réponse par la tonique et le mode sur une nouvelle ligne, formatés comme suit : 'TONIQUE MODE'.\n"
        "La tonique doit systématiquement être renvoyé sous sa forme lettrée."
        f"Listes des modes acceptés: {', '.join(MODES_DATA.keys())}"
        "Exemple de sortie :\n"
        "Explication...\n"
        "C Ionian\n\n"
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
