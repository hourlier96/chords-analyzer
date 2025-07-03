<template>
  <div class="builder-container">
    <div class="progression-builder">
      <draggable
        v-model="progression"
        item-key="id"
        class="draggable-container"
        ghost-class="ghost"
      >
        <template #item="{ element: chord }">
          <div class="chord-slot">
            <button class="chord-button" @click="startEditing(chord)">
              {{ getChordDisplayName(chord) }}
            </button>
            <button class="remove-button" @click="removeChord(chord.id)">
              ×
            </button>

            <div v-if="editingChordId === chord.id" class="editor-popover">
              <select v-model="chord.root" class="root-select">
                <option
                  v-for="note in NOTES"
                  :key="note"
                  :value="note.split(' / ')[0]"
                >
                  {{ note }}
                </option>
              </select>

              <div class="quality-selector">
                <div class="category-tabs">
                  <button
                    v-for="group in QUALITIES"
                    :key="group.label"
                    @click="activeQualityCategory = group.label"
                    :class="{ active: activeQualityCategory === group.label }"
                  >
                    {{ group.label }}
                  </button>
                </div>
                <div class="options-grid">
                  <button
                    v-for="option in activeQualityOptions"
                    :key="option.value"
                    @click="chord.quality = option.value"
                    :class="{ active: chord.quality === option.value }"
                  >
                    {{ option.text }}
                  </button>
                </div>
              </div>
              <button @click="stopEditing" class="close-editor">OK</button>
            </div>
          </div>
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
          <!-- Remplacé v-progress-circular par une animation SVG pour la compatibilité -->
          <svg
            class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            ></circle>
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          Analyse en cours...
        </template>
        <template v-else> Analyser la Progression </template>
      </button>
    </div>

    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, defineEmits, computed } from "vue";
import { useAnalysisStore } from "@/stores/analysis.js";
import { QUALITIES, NOTES } from "@/constants.js";
import draggable from "vuedraggable";

const analysisStore = useAnalysisStore();

const props = defineProps({
  modelValue: { type: Array, required: true },
  isLoading: { type: Boolean, default: false },
  error: { type: String, default: "" },
});

const emit = defineEmits(["update:modelValue", "analyze"]);

const editingChordId = ref(null);
const activeQualityCategory = ref(null);

const progression = computed({
  get: () => props.modelValue,
  set: (newValue) => {
    emit("update:modelValue", newValue);
  },
});

const activeQualityOptions = computed(() => {
  if (!activeQualityCategory.value) return [];
  const group = QUALITIES.find((g) => g.label === activeQualityCategory.value);
  return group ? group.options : [];
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

function startEditing(chord) {
  editingChordId.value = chord.id;
  let foundCategory = null;
  if (chord.quality !== null) {
    for (const group of QUALITIES) {
      if (group.options.some((opt) => opt.value === chord.quality)) {
        foundCategory = group.label;
        break;
      }
    }
  }
  activeQualityCategory.value =
    foundCategory || (QUALITIES.length > 0 ? QUALITIES[0].label : null);
}

function stopEditing() {
  editingChordId.value = null;
  activeQualityCategory.value = null;
}

function getChordDisplayName(chord) {
  return `${chord.root}${chord.quality}`;
}

function onAnalyze() {
  emit("analyze", progression.value);
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
.draggable-container {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}
.chord-slot {
  position: relative;
  cursor: grab;
}
.ghost {
  opacity: 0.5;
  background: #4a4a4a;
  border: 2px dashed #007bff;
}
.chord-button {
  padding: 1rem 1.5rem;
  font-size: 1.5rem;
  font-weight: 600;
  border-radius: 8px;
  border: 2px solid #555;
  background-color: #3c3c3c;
  color: white;
  min-width: 100px;
  transition: all 0.2s;
}
.chord-button:hover {
  border-color: #007bff;
}
.remove-button {
  position: absolute;
  top: -10px;
  right: -10px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: none;
  background-color: #ff4d4d;
  color: white;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
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

.editor-popover {
  position: absolute;
  top: calc(100% + 10px);
  left: 50%;
  transform: translateX(-50%);
  background-color: #4a4a4a;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 1rem; /* Espace augmenté */
  width: 500px; /* Largeur augmentée */
}

.root-select {
  background-color: #3c3c3c;
  color: white;
  border: 1px solid #555;
  padding: 0.5rem;
  border-radius: 4px;
  width: 100%;
}

.quality-selector {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.category-tabs {
  display: flex;
  overflow-x: auto;
  padding-bottom: 8px;
  scrollbar-width: thin;
  scrollbar-color: #888 #4a4a4a;
}
.category-tabs::-webkit-scrollbar {
  height: 4px;
}
.category-tabs::-webkit-scrollbar-track {
  background: #4a4a4a;
}
.category-tabs::-webkit-scrollbar-thumb {
  background-color: #888;
  border-radius: 2px;
}

.category-tabs button {
  flex-shrink: 0;
  padding: 0.25rem 0.75rem;
  margin-right: 0.5rem;
  border-radius: 1rem;
  border: 1px solid transparent;
  background-color: #5f5f5f;
  color: #ddd;
  font-size: 0.8rem;
  transition: all 0.2s;
  cursor: pointer;
}
.category-tabs button:hover {
  background-color: #777;
}
.category-tabs button.active {
  background-color: #007bff;
  color: white;
  font-weight: bold;
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(65px, 1fr));
  gap: 0.5rem;
  max-height: 140px;
  overflow-y: auto;
  padding: 0.25rem;
}
.options-grid::-webkit-scrollbar {
  width: 4px;
}
.options-grid::-webkit-scrollbar-thumb {
  background-color: #888;
  border-radius: 2px;
}

.options-grid button {
  width: 70px;
  padding: 0.5rem 0.25rem;
  border-radius: 4px;
  border: 1px solid #5f5f5f;
  background-color: #3c3c3c;
  color: #ddd;
  font-size: 0.9rem;
  transition: all 0.2s;
  cursor: pointer;
}
.options-grid button:hover {
  border-color: #007bff;
  color: white;
}
.options-grid button.active {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
  font-weight: bold;
}

.close-editor {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background-color: #007bff;
  border: 1px solid #007bff;
  color: white;
  border-radius: 4px;
  cursor: pointer;
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
