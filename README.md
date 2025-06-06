# Chords generator

I. Cush chords

Heavily inspired from [Cush chords game from Open Studio](https://www.youtube.com/watch?v=7PVOVYwVAi4&ab_channel=OpenStudio)

From a chord progression, provide all available substitutions using borrowed chords from all major modes.

![image](https://github.com/user-attachments/assets/fbcda3d0-5dad-4b9b-a1a6-cdd56a61e80c)

II. Diatonic substitutions

From a chord progression, provide all available substitutions with same harmonical functions

Tonic          I, vi, iii  Stability
Sub-dominant   ii, IV      Transition, move to dominant
Dominant       V, vii°     Tension, call to the tonic

In progress

## Installation

Install requirements.txt depdencies first with:

```bash
# Add any virtualenv first

pip install -r requirements.txt
```

## Run

```python
python3 main.py
```

To enable the mode to be clearly detected, the chord progression provided must be diatonic.

Tonic can be specified manually as parameter (when progression doesn't start with degree 'I')

## Tests

Mode detection has been tested across multiple diatonic chords progressions.

For ambiguous chords progressions, first chords is considered as first degree (I)

```bash
pytest -vs
```
