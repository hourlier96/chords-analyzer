# Chords generator

I. Modal substitution

From a chord progression, provide an exhaustive analysis of each chord, including its quality, borrowed chords, substitutions and more !

- Secondary dominants
- Triton substitutions
- Parralel Modes substitutions
- Modal harmonization substitutions

## Installation

Install requirements.txt dependencies first with:

```bash
# Add any virtualenv first

pip install -r requirements.txt
```

## Run

```bash

uvicorn app.main:app --reload
```

## Tests

Tonic detection, mode detection, and chords substitutions have been tested in an exhaustive way.

```bash
pytest -vs
```
