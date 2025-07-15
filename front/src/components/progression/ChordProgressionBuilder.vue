<template>
  <div class="builder-container">
    <div class="main-toolbar">
      <div class="left-controls">
        <PlayerControls
          :is-playing="isPlaying"
          v-model:time-signature="timeSignature"
          v-model:is-metronome-active="isMetronomeActive"
          v-model:is-looping="isLooping"
          @play="playEntireProgression"
          @stop="stopSound"
        />
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

    <div class="builder-grid-layout">
      <div class="footer-controls">
        <button v-if="!showQuickImport" class="add-button" @click="addChord()">
          +
        </button>
        <button
          v-if="!showQuickImport"
          class="add-button"
          @click="showQuickImport = true"
        >
          <v-icon :icon="mdiKeyboard" />
        </button>
        <div v-if="showQuickImport">
          <input
            type="text"
            v-model="quickImportText"
            placeholder="Ex: Cmaj7 G7"
            class="quick-import-input"
            @keyup.enter="processQuickImport"
          />
          <div class="quick-import-buttons">
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
        </div>
        <v-tooltip
          v-if="!showQuickImport"
          location="top"
          text="Reset la progression"
        >
          <template #activator="{ props }">
            <button v-bind="props" @click="removeAllChords" class="add-button">
              <v-icon :icon="mdiClose" />
            </button>
          </template>
        </v-tooltip>
      </div>

      <div class="progression-grid-container">
        <TimelineGrid
          :total-beats="totalBeats"
          :beats-per-measure="beatsPerMeasure"
          :beat-width="BEAT_WIDTH"
          :is-playing="isPlaying"
          :playhead-position="playheadPosition"
        />

        <div
          class="chords-track"
          :style="{
            '--total-beats': totalBeats,
            '--beat-width': `${BEAT_WIDTH}px`,
          }"
        >
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
                :class="{ 'is-playing-halo': index === currentlyPlayingIndex }"
              >
                <ChordCard
                  :modelValue="chord"
                  :beat-width="BEAT_WIDTH"
                  @update:modelValue="
                    (newChord) => updateChord(index, newChord)
                  "
                  :is-editing="editingChordId === chord.id"
                  :piano="piano"
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

        <button
          class="analyze-icon-button"
          @click="onAnalyze"
          :disabled="
            isLoading || progression.length === 0 || isProgressionUnchanged
          "
          aria-label="Analyser la progression"
        >
          <template v-if="isLoading">
            <v-progress-circular
              indeterminate
              color="white"
              size="20"
              width="2"
            />
          </template>
          <template v-else>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
          </template>
        </button>

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
    </div>
    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import draggable from "vuedraggable";
import { mdiKeyboard, mdiCheck, mdiClose, mdiPiano } from "@mdi/js";

import { BEAT_WIDTH, useStatePlayer } from "@/composables/useStatePlayer.js";
import { piano, getNotesForChord, getNotesAsMidi } from "@/sampler.js";
import { sleep } from "@/utils.js";
import { useTempoStore } from "@/stores/tempo.js";
import { useAnalysisStore } from "@/stores/analysis.js";

import PianoKeyboard from "@/components/common/PianoKeyboard.vue";
import ChordCard from "@/components/progression/ChordCard.vue";
import TimelineGrid from "@/components/common/TimelineGrid.vue";
import PlayerControls from "@/components/common/PlayerControls.vue";

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
const showQuickImport = ref(false);
const quickImportText = ref("");

const playChordItem = async ({ item }) => {
  if (!item) return;
  piano.play(item);
  selectedChordNotes.value = getNotesForChord(item);
  const chordDurationMs = item.duration * tempoStore.beatDurationMs;
  await sleep(chordDurationMs);
};

const progression = computed({
  get: () => props.modelValue,
  set: (newValue) => {
    emit("update:modelValue", newValue);
  },
});

const {
  playheadPosition,
  beatsPerMeasure,
  totalBeats,
  isPlaying,
  currentlyPlayingIndex,
  timeSignature,
  isMetronomeActive,
  isLooping,
  playEntireProgression,
  stopSound,
} = useStatePlayer(progression, {
  onPlayItemAsync: playChordItem,
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

const progressionWithPositions = computed(() => {
  let currentBeat = 1;
  return progression.value.map((chord) => {
    const start = currentBeat;
    currentBeat += chord.duration;
    return { ...chord, start };
  });
});

function onDragEnd(event) {
  const { oldIndex, newIndex } = event;
  const newProgression = [...progression.value];
  const [movedItem] = newProgression.splice(oldIndex, 1);
  newProgression.splice(newIndex, 0, movedItem);
  progression.value = newProgression;
}

function addChord() {
  const newChord = {
    id: Date.now(),
    root: "C",
    quality: "",
    inversion: 0,
    duration: 2,
  };
  progression.value = [...progression.value, newChord];
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

/**
 * Calcule le coût de transition
 */
function calculateMusicalCost(notesA, notesB, weights) {
  if (notesA.length === 0 || notesB.length === 0) return Infinity;
  const sortedA = [...notesA].sort((a, b) => a - b);
  const sortedB = [...notesB].sort((a, b) => a - b);
  const sopranoMove = Math.abs(
    sortedA[sortedA.length - 1] - sortedB[sortedB.length - 1]
  );
  const sopranoCost = sopranoMove * weights.soprano;
  const bassMove = Math.abs(sortedA[0] - sortedB[0]);
  const bassCost = bassMove * weights.bass;
  let overallDistance = 0;
  const len = Math.min(sortedA.length, sortedB.length);
  for (let i = 0; i < len; i++) {
    overallDistance += Math.abs(sortedA[i] - sortedB[i]);
  }
  const overallCost = (overallDistance / len) * weights.overall;
  return sopranoCost + bassCost + overallCost;
}

/**
 * Traite une chaîne d'accords en choisissant le meilleur "voicing" (inversion/octave)
 * en se basant sur le fonctionnement spécifique de getNotesAsMidi.
 */
function processQuickImport() {
  if (!quickImportText.value.trim()) return;

  const WEIGHTS = { soprano: 3.0, bass: 2.0, overall: 1.0 };
  const REPEATED_BASS_PENALTY = 10;

  const chordStrings = quickImportText.value
    .split(/[; -]/)
    .map((s) => s.trim())
    .filter((s) => s);
  if (chordStrings.length === 0) {
    cancelQuickImport();
    return;
  }

  const newChords = [];
  let previousChordNotes =
    progression.value.length > 0
      ? getNotesAsMidi(progression.value[progression.value.length - 1])
      : null;

  for (const chordStr of chordStrings) {
    const baseChord = parseChordString(chordStr);
    if (!baseChord) continue;

    if (!previousChordNotes) {
      const firstChord = { ...baseChord };
      // Inversion de base différente selon la note, pour "centrer"
      if (["C", "C#", "D", "D#", "E"].includes(baseChord.root)) {
        firstChord.inversion = 1;
      } else {
        firstChord.inversion = 0;
      }

      newChords.push(firstChord);
      previousChordNotes = getNotesAsMidi(firstChord);
      continue;
    }

    let bestInversion = 0;
    let bestNotesForNextIteration = [];
    let minCost = Infinity;

    const rootPositionNotes = getNotesAsMidi({ ...baseChord, inversion: 0 });
    // Le nombre d'inversions uniques par octave (3 pour une triade, 4 pour un accord 7).
    const voicingsPerOctave = rootPositionNotes.length;

    // On explore une large plage de "voicings" (inversions) sur plusieurs octaves.
    // Par exemple, de -3 à +6 pour une triade, couvrant l'octave en dessous,
    // l'octave de base et l'octave au-dessus.
    const searchRangeStart = -voicingsPerOctave;
    const searchRangeEnd = 2 * voicingsPerOctave;

    for (let i = searchRangeStart; i < searchRangeEnd; i++) {
      // On demande directement le voicing `i` à la fonction. Pas de décalage manuel.
      const currentNotes = getNotesAsMidi({ ...baseChord, inversion: i });
      if (!currentNotes || currentNotes.length === 0) continue;

      let cost = calculateMusicalCost(
        previousChordNotes,
        currentNotes,
        WEIGHTS
      );

      const previousBass = Math.min(...previousChordNotes);
      const currentBass = Math.min(...currentNotes);
      if (currentBass === previousBass) {
        cost += REPEATED_BASS_PENALTY;
      }

      if (cost < minCost) {
        minCost = cost;
        bestInversion = i;
        bestNotesForNextIteration = currentNotes;
      }
    }

    const finalChord = { ...baseChord, inversion: bestInversion };
    newChords.push(finalChord);
    previousChordNotes = bestNotesForNextIteration;
  }

  if (newChords.length > 0) {
    progression.value = [...progression.value, ...newChords];
  }

  cancelQuickImport();
}
function cancelQuickImport() {
  showQuickImport.value = false;
  quickImportText.value = "";
}
</script>

<style scoped>
.builder-container {
  background-color: #2f2f2f;
  padding: 1rem 1rem;
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

.builder-grid-layout {
  display: flex;
  align-items: center;
  gap: 5px;
}

.progression-grid-container {
  flex-grow: 1;
  overflow-x: auto;
  padding: 0.5rem;
  background-color: #252525;
  border: 1px solid #444;
  border-radius: 8px;
}

.chords-track {
  display: grid;
  grid-template-columns: repeat(var(--total-beats, 8), var(--beat-width));
  grid-auto-rows: minmax(100px, auto);
  align-items: stretch;
  min-height: 110px;
}

.draggable-container {
  display: contents;
}

.chord-wrapper {
  height: 100%;
  display: flex;
  align-items: center;
}

.is-playing-halo .chord-slot {
  box-shadow: 0 0 20px 5px rgba(253, 203, 110, 0.7);
  border-radius: 12px;
}

.ghost {
  opacity: 0.5;
  background: #4a4a4a;
  border: 2px dashed #007bff;
  border-radius: 8px;
}

.footer-controls {
  display: flex;
  flex-direction: column;
  padding-right: 1rem;
  gap: 10px;
}

.add-button {
  width: 35px;
  height: 35px;
  font-size: 16px;
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

.quick-import-input {
  background-color: #3c3c3c;
  border: 1px solid #555;
  color: white;
  border-radius: 6px;
  padding: 0.6rem 1rem;
  width: 150px;
  text-align: center;
}
.quick-import-input::placeholder {
  color: #888;
}
.quick-import-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  margin-top: 10px;
}
.quick-import-button {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  border: none;
  background-color: #4caf50;
  color: white;
  cursor: pointer;
}
.quick-import-button.cancel {
  background-color: #f44336;
}

.analyze-section-container {
  margin-top: 1rem;
  display: flex;
  justify-content: center;
}

.model-selector {
  display: flex;
  align-items: center;
  gap: 5px;
  background-color: #252525;
  border-radius: 8px;
  padding: 5px;
  border: 1px solid #444;
}

.analyze-icon-button {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: none;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease-in-out;
}

.analyze-icon-button:not(:disabled):hover {
  background-color: #0056b3;
}

.analyze-icon-button:disabled {
  background-color: #555;
  cursor: not-allowed;
  color: #888;
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
.radio-label {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  color: #bbb;
  background-color: transparent;
  font-size: 0.9rem;
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
  background-color: #007bff;
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
