# Chords generator

I. Modal substitution

Heavily inspired from [Cush chords game from Open Studio](https://www.youtube.com/watch?v=7PVOVYwVAi4&ab_channel=OpenStudio)

From a chord progression, provide all available substitutions using borrowed chords from all major modes.

![image](https://github.com/user-attachments/assets/fbcda3d0-5dad-4b9b-a1a6-cdd56a61e80c)

## Installation

Install requirements.txt depdencies first with:

```bash
# Add any virtualenv first

pip install -r requirements.txt
```

## Run

```bash
python3 prompt_display.py.         # Show substitutions in terminal

uvicorn app.main:app --reload      # Provide an FastAPI application 
```

## Tests

Tonic detection, mode detection, and chords substitutions have been tested in an exhaustive way.

```bash
pytest -vs
```
