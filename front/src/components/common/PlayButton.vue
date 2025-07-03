<template>
  <button class="listen-button" @click.stop="playArpeggio">
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      width="20"
      height="20"
    >
      <path d="M8 5v14l11-7z" />
    </svg>
  </button>
</template>

<script setup>
import { CHORD_FORMULAS } from "@/constants.js";
import * as Tone from "tone";

const props = defineProps({
  // L'objet accord contenant la fondamentale (root) et la qualité (quality)
  chord: { type: Object, required: true },
  // L'instance du sampler Tone.js partagée
  piano: { type: Object, required: true },
});

// Liste des notes pour le calcul des intervalles
const ALL_NOTES_FLAT = [
  "C",
  "C#",
  "D",
  "D#",
  "E",
  "F",
  "F#",
  "G",
  "G#",
  "A",
  "A#",
  "B",
];

/**
 * Calcule les notes d'un accord à partir de sa fondamentale et de sa qualité.
 * @param {number} octave - L'octave de départ pour les notes.
 * @returns {string[]} Un tableau de notes (ex: ["C4", "E4", "G4"]).
 */
function getNotesForChord(octave = 4) {
  const intervals = CHORD_FORMULAS[props.chord.quality];
  if (!intervals) return [];

  const rootIndex = ALL_NOTES_FLAT.indexOf(props.chord.root);
  if (rootIndex === -1) return [];

  return intervals.map((interval) => {
    const noteIndex = (rootIndex + interval) % 12;
    const currentOctave = octave + Math.floor((rootIndex + interval) / 12);
    return `${ALL_NOTES_FLAT[noteIndex]}${currentOctave}`;
  });
}

/**
 * Joue les notes de l'accord en arpège.
 */
async function playArpeggio() {
  // S'assure que le contexte audio est démarré (nécessaire sur interaction de l'utilisateur)
  if (Tone.getContext().state !== "running") {
    await Tone.start();
  }

  // Arrête toutes les notes précédemment jouées
  props.piano.releaseAll();

  const notes = getNotesForChord();

  if (notes.length > 0) {
    const now = Tone.now();
    notes.forEach((note, index) => {
      // Joue chaque note de l'arpège avec un léger décalage
      props.piano.triggerAttackRelease(note, "0.5s", now + index * 0.12);
    });
  }
}
</script>

<style scoped>
.listen-button {
  position: absolute;
  bottom: -10px;
  left: -10px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 5;
  transition: background-color 0.2s;
}

.listen-button:hover {
  background-color: #0056b3;
}
</style>
