from typing import Any, Dict, List, Tuple

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modal_substitution.generator import get_degrees_to_borrow, get_substitutions
from app.schema import ChordItem, ProgressionRequest
from app.secondary_dominant.generator import get_secondary_dominant_for_target
from app.tritone_substitution.generator import get_tritone_substitute
from app.utils.borrowed_modes import get_borrowed_chords
from app.utils.chords_analyzer import QualityAnalysisItem, analyze_chord_in_context
from app.utils.common import get_note_from_index, get_note_index
from app.utils.mode_detection_gemini import detect_tonic_and_mode
from constants import MAJOR_MODES_DATA, MODES_DATA

load_dotenv()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze")
def get_all_substitutions(request: ProgressionRequest):
    progression_data: List[ChordItem] = request.chordsData
    model: str = request.model
    if not progression_data:
        return {"error": "Progression cannot be empty"}

    progression = [f"{item.root}{item.quality}" for item in progression_data]
    try:
        # Find tonic with IA
        tonic, mode, explanations = detect_tonic_and_mode(progression, model)
        # tonic, mode, explanations = "A", "Ionian", "blabla"  # Mocked for testing
        detected_tonic_index: int = get_note_index(tonic)

        # Find "foreign" chords from detected mode
        quality_analysis: List[QualityAnalysisItem] = []
        for chord_data in progression_data:
            chord_name = f"{chord_data.root}{chord_data.quality}"
            # Analyze each chord in the context of the detected tonic and mode
            analyzed_chord = analyze_chord_in_context(chord_name, detected_tonic_index, mode)
            # Add additional properties from the request
            analyzed_chord["inversion"] = chord_data.inversion
            analyzed_chord["duration"] = chord_data.duration
            quality_analysis.append(analyzed_chord)

        tonic_name = get_note_from_index(detected_tonic_index)
        borrowed_chords = get_borrowed_chords(quality_analysis, tonic_name, mode)

        # Get degrees to borrow
        degrees_to_borrow: List[int | None] = get_degrees_to_borrow(quality_analysis)

        # Get major modes substitutions from degrees
        substitutions: Dict[str, Dict[str, Any]] = {}
        for mode_name, (_, _, interval) in MAJOR_MODES_DATA.items():
            relative_tonic_index = (detected_tonic_index + interval + 12) % 12
            new_progression = get_substitutions(
                progression,
                relative_tonic_index,
                degrees_to_borrow,
            )
            substitutions[mode_name] = {
                "borrowed_scale": f"{get_note_from_index(relative_tonic_index)} Major",
                "substitution": new_progression,
            }

        # Harmonize all existing modes
        harmonized_chords: Dict[str, List[QualityAnalysisItem]] = {}
        for mode_name, (_, _, _) in MODES_DATA.items():
            tonic_index: int = get_note_index(tonic_name)
            new_progression = get_substitutions(
                progression, tonic_index, degrees_to_borrow, mode_name
            )
            harmonized_chords[mode_name] = [
                analyze_chord_in_context(item["chord"], tonic_index, mode_name)
                for item in new_progression
            ]

        # Get all secondary dominants for all major modes
        secondary_dominants: Dict[str, List[Tuple[str, str, Dict[str, Any]]]] = {}
        for mode_name, substitutions_data in substitutions.items():
            secondary_dominants[mode_name] = []
            for item in substitutions_data["substitution"]:
                secondary_dominant, analysis = get_secondary_dominant_for_target(
                    item["chord"], tonic, mode_name
                )
                secondary_dominants[mode_name].append((secondary_dominant, item["chord"], analysis))

        tritone_substitutions: List[List[Any]] = []
        for chord in progression:
            secondary_dominant, analysis = get_secondary_dominant_for_target(chord, tonic, mode)
            # Correction: on ajoute une clé "mode" par défaut si jamais non itérée
            if mode not in secondary_dominants:
                secondary_dominants[mode] = []
            secondary_dominants[mode].append((secondary_dominant, chord, analysis))

            substitute, analysis = get_tritone_substitute(chord)
            tritone_substitutions.append([chord, substitute, analysis])

        return {
            "tonic": tonic,
            "mode": mode,
            "explanations": explanations,
            "quality_analysis": quality_analysis,
            "borrowed_chords": borrowed_chords,
            "major_modes_substitutions": substitutions,
            "harmonized_chords": harmonized_chords,
            "secondary_dominants": secondary_dominants,
            # "tritone_substitutions": tritone_substitutions,
        }
    except Exception as e:
        raise e


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
