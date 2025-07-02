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
              <select v-model="chord.root">
                <option v-for="note in NOTES" :key="note" :value="note">
                  {{ note }}
                </option>
              </select>
              <select v-model="chord.quality">
                <optgroup
                  v-for="group in QUALITIES"
                  :key="group.label"
                  :label="group.label"
                >
                  <option
                    v-for="option in group.options"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.text }}
                  </option>
                </optgroup>
              </select>
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
          <v-progress-circular
            indeterminate
            size="20"
            width="2"
            color="primary"
            class="mr-2"
          ></v-progress-circular>
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
import draggable from "vuedraggable";

const analysisStore = useAnalysisStore();

const NOTES = [
  "C",
  "C# / Db",
  "D",
  "D# / Eb",
  "E",
  "F",
  "F# / Gb",
  "G",
  "G# / Ab",
  "A",
  "A# / Bb",
  "B",
];
const QUALITIES = [
  {
    label: "Accords Majeurs",
    options: [
      { value: "", text: "Majeur" },
      { value: "maj7", text: "Majeur 7" },
      { value: "maj7#5", text: "Majeur 7#5 (Maj7+5)" },
      { value: "maj9", text: "Majeur 9 (Maj9)" },
    ],
  },
  {
    label: "Accords Mineurs",
    options: [
      { value: "m", text: "Mineur" },
      { value: "m7", text: "Mineur 7" },
      { value: "m(maj7)", text: "Mineur Majeur 7 (mMaj7)" },
      { value: "m6", text: "Mineur 6 (m6)" },
      { value: "m9", text: "Mineur 9 (m9)" },
      { value: "m11", text: "Mineur 11 (m11)" },
    ],
  },
  {
    label: "Accords de Dominante",
    options: [
      { value: "7", text: "Dominant 7" },
      { value: "7b5", text: "Dominant 7♭5" },
      { value: "7#5", text: "Dominant 7♯5" },
      { value: "7b9", text: "Dominant 7♭9" },
      { value: "7#9", text: "Dominant 7♯9" },
      { value: "13", text: "Dominant 13" },
    ],
  },
  {
    label: "Accords Diminués",
    options: [
      { value: "m7b5", text: "Demi-diminué (m7b5)" },
      { value: "dim", text: "Diminué (triade)" },
      { value: "dim7", text: "Diminué 7 (o7)" },
    ],
  },
  {
    label: "Accords Augmentés",
    options: [{ value: "aug", text: "Augmenté (#5)" }],
  },
  {
    label: "Accords Suspendus",
    options: [
      { value: "sus2", text: "Suspended 2 (sus2)" },
      { value: "7sus2", text: "Suspended 2 & 7 minor (7sus2)" },
      { value: "sus4", text: "Suspended 4 (sus4)" },
      { value: "7sus4", text: "Suspended 4 & 7 minor (7sus4)" },
    ],
  },
];

const props = defineProps({
  modelValue: { type: Array, required: true },
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
  if (!analysisStore.lastAnalysis.progression || !analysisStore.hasResult) {
    return false;
  }
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
}

function stopEditing() {
  editingChordId.value = null;
}

function getChordDisplayName(chord) {
  for (const group of QUALITIES) {
    const quality = group.options.find((q) => q.value === chord.quality);
    if (quality) {
      return `${chord.root}${quality.value}`;
    }
  }
  return chord.root;
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
  gap: 0.5rem;
  width: 220px;
}

.editor-popover select {
  border: 1px solid #ccc;
  padding: 4px;
  border-radius: 4px;
}

.editor-popover .close-editor {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background-color: #007bff;
  border: 1px solid;
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
}

.analyze-button:disabled {
  background-color: #555;
  cursor: not-allowed;
}
</style>
