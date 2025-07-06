import { ref } from "vue";
import * as Tone from "tone";
import { ALL_NOTES_FLAT, CHORD_FORMULAS } from "@/constants.js";

const compressor = new Tone.Compressor({
  threshold: -12, // Le seuil à partir duquel la compression s'active
  ratio: 4, // Le ratio de compression (4:1)
}).toDestination();

const eq = new Tone.EQ3({
  low: -2, // Baisser un peu les basses pour éviter un son boueux
  mid: 0,
  high: 2, // Augmenter les aigus pour plus de brillance
});
const reverb = new Tone.Reverb({
  decay: 2.5, // La queue de la réverbération
  wet: 0.3, // La quantité d'effet (0 à 1)
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
}).chain(eq, compressor, reverb);

function noteToMidi(note) {
  const octave = parseInt(note.slice(-1));
  const noteName = note.slice(0, -1);
  const noteIndex = ALL_NOTES_FLAT.indexOf(noteName);
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
  const rootIndex = ALL_NOTES_FLAT.indexOf(chord.root);
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
    return { name: ALL_NOTES_FLAT[noteIndex], octave: octave };
  });

  const inversion = chord.inversion || 0;
  if (inversion > 0 && inversion < notes.length) {
    for (let i = 0; i < inversion; i++) {
      if (notes[i]) notes[i].octave += 1;
    }
  } else if (inversion < 0 && Math.abs(inversion) < notes.length) {
    const numToDrop = Math.abs(inversion);
    for (let i = 0; i < numToDrop; i++) {
      const noteIndex = notes.length - 1 - i;
      if (notes[noteIndex]) notes[noteIndex].octave -= 1;
    }
  }

  return notes
    .sort(
      (a, b) =>
        noteToMidi(`${a.name}${a.octave}`) - noteToMidi(`${b.name}${b.octave}`)
    )
    .map((note) => `${note.name}${note.octave}`);
}

/**
 * Plays a chord (all notes together).
 * @param {object} chord - The chord object with { root, quality }.
 */
piano.playChord = function (chord) {
  this.releaseAll();
  const notes = getNotesForChord(chord);
  if (notes.length > 0) {
    this.triggerAttack(notes);
  }
};

/**
 * Plays a chord as an arpeggio.
 * @param {object} chord - The chord object with { root, quality }.
 */
piano.playArpeggio = function (chord) {
  this.releaseAll();
  const notes = getNotesForChord(chord);
  if (notes.length > 0) {
    const now = Tone.now();
    const baseVelocity = 0.6;
    const velocityIncrement = 0.1;
    notes.forEach((note, index) => {
      const velocity = Math.min(1.0, baseVelocity + index * velocityIncrement);
      this.triggerAttackRelease(note, "0.5s", now + index * 0.2, velocity);
    });
  }
};

export const playbackMode = ref("chords");
/**
 * Sets the playback mode for the piano.
 * @param {'arpeggio' | 'chord'} mode - The desired playback mode.
 */
export function setPlaybackMode(mode) {
  if (mode === "arpeggio" || mode === "chord") {
    playbackMode.value = mode;
  }
}

/**
 * Plays a chord based on the current playbackMode.
 * @param {object} chord - The chord object with { root, quality }.
 */

piano.play = function (chord) {
  if (playbackMode.value === "arpeggio") {
    piano.playArpeggio(chord);
  } else {
    piano.playChord(chord);
  }
};
