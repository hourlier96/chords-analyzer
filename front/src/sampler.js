import * as Tone from "tone";
import { useTempoStore } from "@/stores/tempo.js";
import { useSettingsStore } from "@/stores/settings.js";
import {
  NOTES_FLAT,
  ENHARMONIC_EQUIVALENTS,
  CHORD_FORMULAS,
} from "@/constants.js";

const settingsStore = useSettingsStore();

const compressor = new Tone.Compressor({
  threshold: -12,
  ratio: 4,
}).toDestination();

const eq = new Tone.EQ3({
  low: -2,
  mid: 0,
  high: 2,
});
const reverb = new Tone.Reverb({
  decay: 2.5,
  wet: 0.3,
  preDelay: 0.01,
}).toDestination();

export const piano = new Tone.Sampler({
  urls: {
    A1: "A1.mp3",
    C2: "C2.mp3",
    "D#2": "Ds2.mp3",
    "F#2": "Fs2.mp3",
    A2: "A2.mp3",
    C3: "C3.mp3",
    "D#3": "Ds3.mp3",
    "F#3": "Fs3.mp3",
    A3: "A3.mp3",
    C4: "C4.mp3",
    "D#4": "Ds4.mp3",
    "F#4": "Fs4.mp3",
    A4: "A4.mp3",
    C5: "C5.mp3",
    "D#5": "Ds5.mp3",
    "F#5": "Fs5.mp3",
    A5: "A5.mp3",
    C6: "C6.mp3",
    "D#6": "Ds6.mp3",
    "F#6": "Fs6.mp3",
    A6: "A6.mp3",
    C7: "C7.mp3",
  },
  release: 1.2,
  baseUrl: "https://tonejs.github.io/audio/salamander/",
}).chain(eq, compressor);

compressor.connect(reverb);
const DEFAULT_REVERB_WET = reverb.wet.value;
// Définis une valeur de réverbération plus élevée pour l'arpège
const ARPEGGIO_REVERB_WET = 0.8; // Tu peux ajuster cette valeur (entre 0.0 et 1.0)

function noteToMidi(note) {
  const octave = parseInt(note.slice(-1));
  const noteName = note.slice(0, -1);
  const noteIndex = NOTES_FLAT.indexOf(noteName);
  return octave * 12 + noteIndex;
}

/**
 * Calculates the notes for a given chord, keeping them in a balanced, centered range.
 * @param {object} chord - The chord object with { root, quality }.
 * @returns {string[]} An array of notes (e.g., ["C4", "E4", "G4"]).
 */
export function getNotesForChord(chord, previousNotes = null) {
  const intervals = CHORD_FORMULAS[chord.quality];
  if (!intervals) return [];

  let rootIndex = NOTES_FLAT.indexOf(chord.root);
  if (rootIndex === -1 && ENHARMONIC_EQUIVALENTS[chord.root]) {
    const enharmonic = ENHARMONIC_EQUIVALENTS[chord.root];
    rootIndex = NOTES_FLAT.indexOf(enharmonic);
  }
  if (rootIndex === -1) return [];

  let baseOctave;
  if (!previousNotes || previousNotes.length === 0) {
    baseOctave = 3;
  } else {
    const previousRootMidi = noteToMidi(previousNotes[0]);
    let bestOctave = -1;
    let minDistance = Infinity;
    for (let octave = 2; octave <= 5; octave++) {
      const currentRootMidi = octave * 12 + rootIndex;
      const distance = Math.abs(currentRootMidi - previousRootMidi);
      if (distance < minDistance) {
        minDistance = distance;
        bestOctave = octave;
      }
    }
    baseOctave = bestOctave;
  }

  let notes = intervals.map((interval) => {
    const noteIndex = (rootIndex + interval) % 12;
    const octave = baseOctave + Math.floor((rootIndex + interval) / 12);
    return { name: NOTES_FLAT[noteIndex], octave: octave };
  });

  const inversion = chord.inversion || 0;
  const numNotes = notes.length;

  if (numNotes > 0) {
    // Calcule le décalage d'octave global pour l'accord entier.
    // Ex: pour un accord de 3 notes, inversion 3 -> décalage de +1 octave.
    const octaveShift = Math.floor(inversion / numNotes);

    // Calcule le renversement structurel (ex: 0, 1, ou 2 pour un accord de 3 notes).
    // Gère correctement les valeurs positives et négatives.
    const effectiveInversion = ((inversion % numNotes) + numNotes) % numNotes;

    // Applique le renversement en montant d'une octave les premières notes.
    for (let i = 0; i < effectiveInversion; i++) {
      if (notes[i]) {
        notes[i].octave += 1;
      }
    }

    // Applique le décalage d'octave global à toutes les notes.
    if (octaveShift !== 0) {
      notes.forEach((note) => {
        note.octave += octaveShift;
      });
    }
  }

  return notes
    .sort(
      (a, b) =>
        noteToMidi(`${a.name}${a.octave}`) - noteToMidi(`${b.name}${b.octave}`)
    )
    .map((note) => `${note.name}${note.octave}`);
}

export function getNotesAsMidi(chord, previousNotes = null) {
  const notesAsStrings = getNotesForChord(chord, previousNotes);
  return notesAsStrings.map((noteStr) => noteToMidi(noteStr));
}

/**
 * Plays a chord (all notes together).
 * @param {object} chord - The chord object with { root, quality }.
 */
piano.playChord = function (chord) {
  this.releaseAll();
  const notes = getNotesForChord(chord);
  if (notes.length > 0) {
    reverb.wet.value = DEFAULT_REVERB_WET; 
    this.triggerAttack(notes);
  }
};

/**
 * Joue un accord en arpège en tenant compte du tempo.
 * @param {string} chord - Le nom de l'accord à jouer.
 */
piano.playArpeggio = function (chord) {
  const tempoStore = useTempoStore();
  this.releaseAll();
  const notes = getNotesForChord(chord);

  if (notes.length > 0) {
    const now = Tone.now();
    const quarterNoteDuration = 60 / tempoStore.bpm;

    const totalArpeggioOccupancyDuration = quarterNoteDuration;
    const arpeggioTriggerInterval = notes.length > 1 
        ? totalArpeggioOccupancyDuration / (notes.length -1)
        : 0; 
    const noteDuration = arpeggioTriggerInterval > 0 ? arpeggioTriggerInterval *1.20 : totalArpeggioOccupancyDuration;

    const baseVelocity = 0.45;
    const maxVelocity = 0.9;
    reverb.wet.value = ARPEGGIO_REVERB_WET;
    notes.forEach((note, index) => {
      const velocity = baseVelocity + (maxVelocity - baseVelocity) * (index / (notes.length - 1 || 1));
      const startTime = now + index * arpeggioTriggerInterval;

      this.triggerAttackRelease(note, noteDuration, startTime, velocity);
    });
  }
};

/**
 * Plays a chord based on the current audioMode.
 * @param {object} chord - The chord object with { root, quality }.
 */

piano.play = function (chord) {
  if (settingsStore.audioMode === "arpeggio") {
    piano.playArpeggio(chord);
  } else {
    piano.playChord(chord);
  }
};
