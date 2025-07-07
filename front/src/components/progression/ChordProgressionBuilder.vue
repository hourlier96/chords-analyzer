<template>
  <div class="builder-container">
    <div class="progression-builder">
      <PianoKeyboard :active-notes="selectedChordNotes" />

      <div class="main-row">
        <div class="header-controls">
          <div v-if="!isPlaying" class="d-flex ga-2">
            <v-tooltip location="top" text="Lire la progression">
              <template #activator="{ props }">
                <button
                  v-bind="props"
                  @click="playEntireProgression"
                  class="control-icon-button"
                >
                  <v-icon :icon="mdiPlay" />
                </button>
              </template>
            </v-tooltip>
          </div>
          <v-tooltip v-else location="top" text="Stopper la lecture">
            <template #activator="{ props }">
              <button
                v-bind="props"
                @click="stopSound()"
                class="control-icon-button"
              >
                <v-icon :icon="mdiStop" />
              </button>
            </template>
          </v-tooltip>
          <v-tooltip location="top" text="Reset la progression">
            <template #activator="{ props }">
              <button
                v-bind="props"
                @click="removeAllChords()"
                class="control-icon-button"
              >
                <v-icon :icon="mdiClose" />
              </button>
            </template>
          </v-tooltip>
        </div>

        <draggable
          v-model="progression"
          item-key="id"
          class="draggable-container"
          ghost-class="ghost"
        >
          <template #item="{ element: chord, index }">
            <ChordCard
              :modelValue="chord"
              @update:modelValue="(newChord) => updateChord(index, newChord)"
              :is-editing="editingChordId === chord.id"
              :piano="piano"
              :class="{ 'is-playing-halo': index === currentlyPlayingIndex }"
              @remove="removeChord(chord.id)"
              @start-editing="startEditing(chord)"
              @stop-editing="stopEditing"
            />
          </template>
          <template #footer>
            <div class="footer-controls">
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
                  placeholder="Ex: Cmaj7; G7; Am7; F"
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
            </div>
          </template>
        </draggable>
      </div>
    </div>

    <div class="analyze-button-container">
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
// Le script reste exactement le même
import { ref, computed } from "vue";
import draggable from "vuedraggable";
import * as Tone from "tone";
import { mdiPlay, mdiStop, mdiKeyboard, mdiCheck, mdiClose } from "@mdi/js";

import { piano, getNotesForChord } from "@/sampler.js";
import { sleep } from "@/utils.js";
import { useAnalysisStore } from "@/stores/analysis.js";
import PianoKeyboard from "@/components/common/PianoKeyboard.vue";
import ChordCard from "@/components/progression/ChordCard.vue";

const analysisStore = useAnalysisStore();

const props = defineProps({
  modelValue: { type: Array, required: true },
  isLoading: { type: Boolean, default: false },
  error: { type: String, default: "" },
});

const emit = defineEmits(["update:modelValue", "analyze"]);

const editingChordId = ref(null);
const selectedChordNotes = ref([]);
const isPlaying = ref(false);
const currentlyPlayingIndex = ref(null);
const showQuickImport = ref(false);
const quickImportText = ref("");

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
    JSON.stringify(analysisStore.lastAnalysis.progression)
  );
});

function addChord() {
  const newChord = { id: Date.now(), root: "C", quality: "", inversion: 0 };
  progression.value = [...progression.value, newChord];
  startEditing(newChord);
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

  return { id: Date.now() + Math.random(), root, quality, inversion: 0 };
}

function removeAllChords() {
  progression.value = [];
  stopEditing();
  selectedChordNotes.value = [];
}

function processQuickImport() {
  if (!quickImportText.value.trim()) return;

  const newChords = quickImportText.value
    .split(";")
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
  if (isPlaying.value) return;

  if (Tone.getContext().state !== "running") {
    await Tone.start();
  }

  isPlaying.value = true;
  try {
    for (const [index, item] of progression.value.entries()) {
      if (!isPlaying.value) break;
      if (!item) continue;
      currentlyPlayingIndex.value = index;
      piano.play(item);
      selectedChordNotes.value = getNotesForChord(item);
      await sleep(1000);
    }
    currentlyPlayingIndex.value = null;
  } catch (error) {
    console.error("Error during playback:", error);
  } finally {
    isPlaying.value = false;
  }
};

function stopSound() {
  isPlaying.value = false;
  piano.releaseAll();
  currentlyPlayingIndex.value = null;
}
</script>

<style scoped>
.builder-container {
  background-color: #2f2f2f;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

/* MODIFIÉ : Le conteneur principal devient une colonne flex */
.progression-builder {
  display: flex;
  flex-direction: column;
  gap: 1.5rem; /* Espace entre le piano et la rangée principale */
}

/* NOUVEAU : La rangée principale qui aligne les contrôles et les accords */
.main-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* MODIFIÉ : Le conteneur des boutons est maintenant un élément flex */
.header-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0; /* Empêche les boutons de se compresser */
}

.header-controls .control-icon-button {
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
}
.header-controls .control-icon-button:hover:not(:disabled) {
  background-color: #5a5a5a;
  border-color: #777;
}

/* MODIFIÉ : La zone des accords peut maintenant s'étendre */
.draggable-container {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
  flex-grow: 1; /* Permet à la zone des accords de prendre l'espace restant */
}
.is-playing-halo {
  box-shadow: 0 0 20px 5px rgba(253, 203, 110, 0.7);
}
.ghost {
  opacity: 0.5;
  background: #4a4a4a;
  border: 2px dashed #007bff;
}
.footer-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}
.add-button {
  width: 50px;
  height: 50px;
  font-size: 25px;
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
  width: 300px;
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
.analyze-button-container {
  margin-top: 2rem;
  text-align: center;
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
