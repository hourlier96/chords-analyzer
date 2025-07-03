<template>
  <div class="builder-container">
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
import { useAnalysisStore } from "@/stores/analysis.js";
import draggable from "vuedraggable";
import ChordCard from "./ChordCard.vue"; // Assurez-vous que le chemin est correct

const analysisStore = useAnalysisStore();

const props = defineProps({
  modelValue: { type: Array, required: true },
  piano: { type: Object, required: true },
  isLoading: { type: Boolean, default: false },
  error: { type: String, default: "" },
});

const emit = defineEmits(["update:modelValue", "analyze"]);

const editingChordId = ref(null);

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
  props.piano.play(newChord);
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
</script>

<style scoped>
/* Les styles pour le conteneur principal, .progression-builder, .add-button, etc. restent ici */
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
