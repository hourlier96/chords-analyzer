<template>
  <div class="builder-container">
    <div class="main-toolbar">
      <div class="left-controls">
        <TempoControl />
        <div class="time-signature-selector">
          <v-tooltip location="top" text="Signature Rythmique">
            <template #activator="{ props: tooltipProps }">
              <v-icon :icon="mdiTimelineClockOutline" v-bind="tooltipProps" />
            </template>
          </v-tooltip>
          <label
            v-for="sig in ['3/4', '4/4', '5/4']"
            :key="sig"
            class="radio-label-sm"
            :class="{ active: timeSignature === sig }"
          >
            <input
              type="radio"
              name="time-signature"
              :value="sig"
              :checked="timeSignature === sig"
              @change="timeSignature = sig"
            />
            {{ sig }}
          </label>
        </div>
        <v-tooltip
          location="top"
          :text="
            isMetronomeActive
              ? 'Désactiver le métronome'
              : 'Activer le métronome'
          "
        >
          <template #activator="{ props }">
            <button
              v-bind="props"
              @click="isMetronomeActive = !isMetronomeActive"
              class="control-icon-button"
              :class="{ 'is-active': isMetronomeActive }"
            >
              <v-icon :icon="mdiMetronome" />
            </button>
          </template>
        </v-tooltip>
        <v-tooltip
          location="top"
          :text="isLooping ? 'Désactiver la loop' : 'Activer la loop'"
        >
          <template #activator="{ props }">
            <button
              v-bind="props"
              @click="isLooping = !isLooping"
              class="control-icon-button"
              :class="{ 'is-active': isLooping }"
            >
              <v-icon :icon="mdiSync" />
            </button>
          </template>
        </v-tooltip>
        <div class="d-flex ga-2">
          <v-tooltip location="top" text="Lire la progression">
            <template #activator="{ props }">
              <button
                v-bind="props"
                @click="playEntireProgression"
                class="control-icon-button"
                :disabled="isPlaying"
              >
                <v-icon :icon="mdiPlay" />
              </button>
            </template>
          </v-tooltip>
          <v-tooltip location="top" text="Stopper la lecture">
            <template #activator="{ props }">
              <button
                v-bind="props"
                @click="stopSound"
                class="control-icon-button"
                :disabled="!isPlaying"
              >
                <v-icon :icon="mdiStop" />
              </button>
            </template>
          </v-tooltip>
        </div>
      </div>
      <div class="right-controls">
        <v-tooltip
          location="top"
          :text="isPianoVisible ? 'Cacher le piano' : 'Afficher le piano'"
        >
          <template #activator="{ props }">
            <button
              v-bind="props"
              @click="isPianoVisible = !isPianoVisible"
              class="control-icon-button"
            >
              <v-icon :icon="mdiPiano" />
            </button>
          </template>
        </v-tooltip>
      </div>
    </div>

    <PianoKeyboard
      v-if="isPianoVisible"
      :active-notes="selectedChordNotes"
      class="mb-6"
    />

    <div class="progression-grid-container">
      <div style="display: flex; flex-direction: row">
        <div
          class="footer-controls"
          :style="{ gridColumn: `${footerControlsStartBeat} / span 2` }"
        >
          <button
            v-if="!showQuickImport"
            class="add-button"
            @click="addChord()"
          >
            +
          </button>
          <v-tooltip location="top" text="Import rapide">
            <template #activator="{ props: tooltipProps }">
              <button
                v-if="!showQuickImport"
                v-bind="tooltipProps"
                class="add-button"
                @click="showQuickImport = true"
              >
                <v-icon :icon="mdiKeyboard" />
              </button>
            </template>
          </v-tooltip>

          <div v-if="showQuickImport" class="quick-import-container">
            <input
              type="text"
              v-model="quickImportText"
              placeholder="Ex: Cmaj7 G7 D Em7"
              class="quick-import-input"
              @keyup.enter="processQuickImport"
            />
            <button @click="processQuickImport" class="quick-import-button">
              <v-icon :icon="mdiCheck" />
            </button>
            <button
              @click="cancelQuickImport"
              class="quick-import-button cancel"
            >
              <v-icon :icon="mdiClose" />
            </button>
          </div>
          <v-tooltip location="top" text="Reset la progression">
            <template #activator="{ props }">
              <button
                v-bind="props"
                @click="removeAllChords"
                class="add-button"
              >
                <v-icon :icon="mdiClose" />
              </button>
            </template>
          </v-tooltip>
        </div>
        <div
          class="progression-grid"
          :style="{
            '--total-beats': totalBeats,
            '--beats-per-measure': beatsPerMeasure,
            '--beat-width': `${BEAT_WIDTH}px`,
          }"
        >
          <div
            v-for="beat in totalBeats"
            :key="`beat-${beat}`"
            class="beat-marker"
            :class="{ 'measure-start': (beat - 1) % beatsPerMeasure === 0 }"
            :style="{ 'grid-column-start': beat }"
          ></div>

          <draggable
            :modelValue="progressionWithPositions"
            @end="onDragEnd"
            item-key="id"
            class="draggable-container"
            ghost-class="ghost"
          >
            <template #item="{ element: chord, index }">
              <div
                class="chord-wrapper"
                :style="{
                  gridColumn: `${chord.start} / span ${chord.duration}`,
                }"
              >
                <ChordCard
                  :modelValue="chord"
                  :beat-width="BEAT_WIDTH"
                  @update:modelValue="
                    (newChord) => updateChord(index, newChord)
                  "
                  :is-editing="editingChordId === chord.id"
                  :piano="piano"
                  :class="{
                    'is-playing-halo': index === currentlyPlayingIndex,
                  }"
                  @remove="removeChord(chord.id)"
                  @start-editing="startEditing(chord)"
                  @stop-editing="stopEditing"
                />
              </div>
            </template>
          </draggable>
        </div>
      </div>
    </div>
    <div class="analyze-section-container">
      <div class="model-selector">
        <label
          :class="{ active: aiModel === 'gemini-2.5-flash' }"
          class="radio-label"
        >
          <input
            type="radio"
            name="ai-model"
            value="gemini-2.5-flash"
            :checked="aiModel === 'gemini-2.5-flash'"
            @change="$emit('update:aiModel', 'gemini-2.5-flash')"
          />
          Modèle Rapide
        </label>
        <label
          :class="{ active: aiModel === 'gemini-2.5-pro' }"
          class="radio-label"
        >
          <input
            type="radio"
            name="ai-model"
            value="gemini-2.5-pro"
            :checked="aiModel === 'gemini-2.5-pro'"
            @change="$emit('update:aiModel', 'gemini-2.5-pro')"
          />
          Modèle Précis
        </label>
      </div>
      <button
        class="analyze-button"
        @click="onAnalyze"
        :disabled="
          isLoading || progression.length === 0 || isProgressionUnchanged
        "
      >
        <template v-if="isLoading">
          <v-progress-circular
            indeterminate
            color="white"
            size="20"
            width="2"
            class="mr-3 inline"
          />
          Analyse en cours...
        </template>
        <template v-else> Analyser la Progression </template>
      </button>
    </div>

    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import draggable from "vuedraggable";
import * as Tone from "tone";
import {
  mdiPlay,
  mdiStop,
  mdiKeyboard,
  mdiCheck,
  mdiClose,
  mdiPiano,
  mdiMetronome,
  mdiSync,
  mdiTimelineClockOutline,
} from "@mdi/js";

import { piano, getNotesForChord } from "@/sampler.js";
import { sleep } from "@/utils.js";
import { useTempoStore } from "@/stores/tempo.js";
import { useAnalysisStore } from "@/stores/analysis.js";
import PianoKeyboard from "@/components/common/PianoKeyboard.vue";
import ChordCard from "@/components/progression/ChordCard.vue";
import TempoControl from "@/components/common/TempoControl.vue";

const BEAT_WIDTH = 60;

const tempoStore = useTempoStore();
const analysisStore = useAnalysisStore();

const props = defineProps({
  modelValue: { type: Array, required: true },
  isLoading: { type: Boolean, default: false },
  error: { type: String, default: "" },
  aiModel: { type: String, required: true },
});

const emit = defineEmits(["update:modelValue", "analyze", "update:aiModel"]);

const isPianoVisible = ref(true);
const editingChordId = ref(null);
const selectedChordNotes = ref([]);
const isPlaying = ref(false);
const currentlyPlayingIndex = ref(null);
const showQuickImport = ref(false);
const quickImportText = ref("");
const isMetronomeActive = ref(true);
const isLooping = ref(true);
const timeSignature = ref("4/4");

const metronome = new Tone.MembraneSynth({
  pitchDecay: 0.5,
  octaves: 0.5,
  envelope: { attack: 0.001, decay: 0.05, sustain: 0, release: 0.05 },
}).toDestination();
metronome.volume.value = -6;

const progression = computed({
  get: () => props.modelValue,
  set: (newValue) => {
    emit("update:modelValue", newValue);
  },
});

const isProgressionUnchanged = computed(() => {
  if (!analysisStore.lastAnalysis.progression || !analysisStore.hasResult)
    return false;
  return (
    JSON.stringify(progression.value) ===
      JSON.stringify(analysisStore.lastAnalysis.progression) &&
    props.aiModel === analysisStore.lastAnalysis.model
  );
});

// MODIFIÉ: Logique pour la grille rythmique
const beatsPerMeasure = computed(() => {
  return parseInt(timeSignature.value.split("/")[0], 10);
});

// Calcule la position de départ de chaque accord
const progressionWithPositions = computed(() => {
  let currentBeat = 1;
  return progression.value.map((chord) => {
    const start = currentBeat;
    currentBeat += chord.duration;
    return { ...chord, start };
  });
});

const footerControlsStartBeat = computed(() => {
  const progressionDuration = progression.value.reduce(
    (sum, chord) => sum + chord.duration,
    0
  );
  return progressionDuration + 1;
});

// Calcule le nombre total de temps nécessaires pour afficher la progression
const totalBeats = computed(() => {
  const progressionDuration = progression.value.reduce(
    (sum, chord) => sum + chord.duration,
    0
  );
  const beatsInMeasure = beatsPerMeasure.value;

  // Si la progression est vide, on affiche une seule mesure
  if (progressionDuration === 0) {
    return beatsInMeasure;
  }

  // Si la progression se termine exactement sur une barre de mesure,
  // on ajoute un temps pour afficher la barre de mesure suivante.
  if (progressionDuration % beatsInMeasure === 0) {
    return progressionDuration + 1;
  }

  // Sinon, on arrondit au nombre de mesures supérieur pour toujours voir des mesures complètes.
  const measures = Math.ceil(progressionDuration / beatsInMeasure);
  return measures * beatsInMeasure;
});
// FIN MODIFICATION

// AJOUTÉ: Gestion du drag & drop pour mettre à jour l'ordre
function onDragEnd(event) {
  const { oldIndex, newIndex } = event;
  const newProgression = [...progression.value];
  const [movedItem] = newProgression.splice(oldIndex, 1);
  newProgression.splice(newIndex, 0, movedItem);
  progression.value = newProgression;
}
// FIN AJOUT

function addChord() {
  const newChord = {
    id: Date.now(),
    root: "C",
    quality: "",
    inversion: 0,
    duration: 2,
  };
  progression.value = [...progression.value, newChord];
  // Pas besoin de startEditing ici, l'utilisateur peut cliquer pour éditer
}

function removeChord(chordId) {
  progression.value = progression.value.filter((c) => c.id !== chordId);
  if (editingChordId.value === chordId) {
    stopEditing();
  }
}

function updateChord(index, newChord) {
  const newProgression = [...progression.value];
  newProgression[index] = newChord;
  progression.value = newProgression;
  piano.play(newChord);
  selectedChordNotes.value = getNotesForChord(newChord);
}

function startEditing(chord) {
  editingChordId.value = chord.id;
  selectedChordNotes.value = getNotesForChord(chord);
}

function stopEditing() {
  editingChordId.value = null;
}

function onAnalyze() {
  emit("analyze", progression.value);
}

function parseChordString(chordStr) {
  if (!chordStr) return null;
  const rootMatch = chordStr.match(/^[A-G][#b]?/);
  if (!rootMatch) return null;
  const root = rootMatch[0];
  const quality = chordStr.substring(root.length);
  return {
    id: Date.now() + Math.random(),
    root,
    quality,
    inversion: 0,
    duration: 2,
  };
}

function removeAllChords() {
  progression.value = [];
  stopEditing();
  selectedChordNotes.value = [];
}

function processQuickImport() {
  if (!quickImportText.value.trim()) return;
  const newChords = quickImportText.value
    .split(/[; -]/)
    .map((str) => str.trim())
    .filter((str) => str)
    .map(parseChordString)
    .filter((chord) => chord);
  if (newChords.length > 0) {
    progression.value = [...progression.value, ...newChords];
  }
  cancelQuickImport();
}

function cancelQuickImport() {
  showQuickImport.value = false;
  quickImportText.value = "";
}

const playEntireProgression = async () => {
  if (isPlaying.value) return; // Le bouton "Play" est déjà désactivé, mais c'est une sécurité.
  if (Tone.getContext().state !== "running") {
    await Tone.start();
  }
  isPlaying.value = true;

  try {
    do {
      for (const [index, item] of progression.value.entries()) {
        if (!isPlaying.value) break;
        if (!item) continue;

        currentlyPlayingIndex.value = index;
        piano.play(item);
        selectedChordNotes.value = getNotesForChord(item);

        if (isMetronomeActive.value) {
          const beatDurationSec = tempoStore.beatDurationMs / 1000;
          for (let beat = 0; beat < item.duration; beat++) {
            if (isPlaying.value) {
              metronome.triggerAttack(
                "C5",
                Tone.now() + beat * beatDurationSec
              );
            }
          }
        }

        const chordDurationMs = item.duration * tempoStore.beatDurationMs;
        await sleep(chordDurationMs);
      }

      if (!isPlaying.value) break;
    } while (isLooping.value);
  } catch (error) {
    console.error("Error during playback:", error);
  } finally {
    stopSound();
  }
};

function stopSound() {
  isPlaying.value = false;
  piano.releaseAll();
  currentlyPlayingIndex.value = null;
}
</script>

<style scoped>
/* ... (Les styles pour main-toolbar, controls, etc. restent les mêmes) ... */
.builder-container {
  background-color: #2f2f2f;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.main-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.left-controls,
.right-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.control-icon-button {
  background-color: #4a4a4a;
  color: #edf2f4;
  border: 1px solid #555;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.2s ease;
}
.control-icon-button:hover:not(:disabled) {
  background-color: #5a5a5a;
  border-color: #777;
}
.control-icon-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.control-icon-button.is-active {
  background-color: #007bff;
  border-color: #0056b3;
}

/* AJOUTÉ: Conteneur pour permettre le défilement horizontal */
.progression-grid-container {
  overflow-x: auto;
  padding-bottom: 1rem; /* Espace pour la barre de défilement */
  background-color: #252525;
  border: 1px solid #444;
  border-radius: 8px;
  padding: 0.5rem;
}

.progression-grid {
  display: grid;
  /* La largeur de colonne utilise maintenant la variable CSS */
  grid-template-columns: repeat(var(--total-beats, 8), var(--beat-width)) auto;
  grid-template-rows: 20px;
  align-items: center;
  min-height: 120px;
  position: relative;
  column-gap: 0;
  overflow: scroll;
}

/* AJOUTÉ: Style pour le conteneur de l'accord */
.chord-wrapper {
  /* Le padding recrée l'espace visuel SANS perturber la grille */
  padding: 0 5px; /* 5px de chaque côté = 10px entre les accords */
  height: 100%; /* S'assure que le wrapper prend toute la hauteur */
  display: flex; /* Utile pour l'alignement interne de ChordCard */
  align-items: center;
}

.beat-marker {
  height: 100%;
  width: 1px; /* Définit l'épaisseur de la ligne */
  background-color: rgba(255, 255, 255, 0.2);
  grid-row: 1; /* S'assure qu'il est sur la même ligne que les accords */
  justify-self: start; /* C'EST LA CORRECTION CLÉ : Aligne la ligne à gauche */
}

/* Le style pour le début de la mesure reste le même */
.beat-marker.measure-start {
  width: 2px;
  background-color: rgba(255, 255, 255, 0.6);
}

/* Le conteneur draggable est maintenant une couche sur la grille */
.draggable-container {
  display: contents; /* Permet aux enfants de se positionner sur la grille parente */
}

/* Le ChordCard est positionné sur la grille */
/* Le style pour grid-column est appliqué dynamiquement */
.is-playing-halo {
  box-shadow: 0 0 20px 5px rgba(253, 203, 110, 0.7);
}
.ghost {
  opacity: 0.5;
  background: #4a4a4a;
  border: 2px dashed #007bff;
  /* S'assure que le fantôme occupe bien l'espace */
  grid-row: 1;
}

/* Les contrôles sont aussi un item de la grille */
.footer-controls {
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: sticky;
  justify-content: center;
  margin-right: 10px;
  padding-right: 6px;
  border-right: 1px dashed grey;
}
/* FIN MODIFICATION */

.add-button {
  width: 30px;
  height: 30px;
  font-size: 15px;
  border-radius: 50%;
  border: 2px dashed #555;
  background-color: transparent;
  color: #888;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
}
.add-button:hover {
  background-color: #3c3c3c;
  color: white;
  border-color: #888;
}

.quick-import-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.quick-import-input {
  background-color: #3c3c3c;
  border: 1px solid #555;
  color: white;
  border-radius: 6px;
  padding: 0.6rem 1rem;
  width: 250px;
}
.quick-import-input::placeholder {
  color: #888;
}
.quick-import-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background-color: #4caf50;
  color: white;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
}
.quick-import-button.cancel {
  background-color: #f44336;
}

.analyze-section-container {
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.model-selector {
  display: flex;
  background-color: #252525;
  border-radius: 8px;
  padding: 5px;
  border: 1px solid #444;
}

.radio-label {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  color: #bbb;
  background-color: transparent;
  font-size: 0.9rem;
}

.radio-label.active {
  background-color: #007bff;
  color: white;
  font-weight: 500;
}

.radio-label:not(.active):hover {
  background-color: #3f3f3f;
}

.radio-label input[type="radio"] {
  display: none;
}

.time-signature-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #252525;
  border-radius: 8px;
  padding: 5px;
  border: 1px solid #444;
  color: #bbb;
}

.radio-label-sm {
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  color: #bbb;
  background-color: transparent;
  font-size: 0.9rem;
}

.radio-label-sm.active {
  background-color: #5a5a5a;
  color: white;
  font-weight: 500;
}

.radio-label-sm:not(.active):hover {
  background-color: #3f3f3f;
}

.radio-label-sm input[type="radio"] {
  display: none;
}

.analyze-button {
  padding: 1rem 2rem;
  font-size: 1.2rem;
  border-radius: 8px;
  border: none;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.analyze-button:disabled {
  background-color: #555;
  cursor: not-allowed;
}
.error-message {
  color: #ff4d4d;
  text-align: center;
  margin-top: 1rem;
}
</style>
