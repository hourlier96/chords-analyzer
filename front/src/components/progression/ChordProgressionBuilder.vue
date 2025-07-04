<template>
  <div class="builder-container">
    <div class="header-controls">
      <v-tooltip v-if="!isPlaying" location="top" text="Lire la progression">
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
    </div>
    <div class="progression-builder">
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
      </draggable>

      <button class="add-button" @click="addChord()">+</button>
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
import { ref, computed } from "vue";
import draggable from "vuedraggable";
import * as Tone from "tone";
import { mdiPlay, mdiStop } from "@mdi/js";

import { piano } from "@/sampler.js";
import { sleep } from "@/utils.js";
import { useAnalysisStore } from "@/stores/analysis.js";
import ChordCard from "@/components/progression/ChordCard.vue";

const analysisStore = useAnalysisStore();

const props = defineProps({
  modelValue: { type: Array, required: true },
  isLoading: { type: Boolean, default: false },
  error: { type: String, default: "" },
});

const emit = defineEmits(["update:modelValue", "analyze"]);

const editingChordId = ref(null);
const isPlaying = ref(false);
const currentlyPlayingIndex = ref(null);

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
  const newChord = { id: Date.now(), root: "C", quality: "" };
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
.progression-builder {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
}

.header-controls {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 10px;
}

.header-controls .control-icon-button {
  background-color: #4a4a4a;
  color: #edf2f4;
  border: 1px solid #555;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  padding: 0;
  font-weight: bold;
  font-family: "Courier New", Courier, monospace;
  font-size: 1rem;
  cursor: pointer;
  transition:
    background-color 0.2s,
    border-color 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
}

.header-controls .control-icon-button:hover:not(:disabled) {
  background-color: #5a5a5a;
  border-color: #777;
}
.draggable-container {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}
.ghost {
  opacity: 0.5;
  background: #4a4a4a;
  border: 2px dashed #007bff;
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
}
.add-button:hover {
  background-color: #3c3c3c;
  color: white;
  border-color: #888;
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
