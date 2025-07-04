<template>
  <div class="chord-slot">
    <PlayButton :chord="chord" />

    <button class="chord-button" @click="$emit('start-editing')">
      {{ chordDisplayName }}
    </button>

    <button class="remove-button" @click="$emit('remove')">×</button>

    <div v-if="isEditing" class="editor-popover">
      <select
        :value="chord.root"
        @change="updateChord('root', $event.target.value)"
        class="root-select"
      >
        <option v-for="note in NOTES" :key="note" :value="note.split(' / ')[0]">
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
            @click="updateChord('quality', option.value)"
            :class="{ active: chord.quality === option.value }"
          >
            {{ option.text }}
          </button>
        </div>
      </div>
      <button @click="$emit('stop-editing')" class="close-editor">OK</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { QUALITIES, NOTES } from "@/constants.js";
import PlayButton from "@/components/common/PlayButton.vue";

const props = defineProps({
  modelValue: { type: Object, required: true },
  isEditing: { type: Boolean, default: false },
});

const emit = defineEmits([
  "update:modelValue",
  "remove",
  "start-editing",
  "stop-editing",
]);

const chord = computed({
  get: () => props.modelValue,
  set: (newValue) => {
    emit("update:modelValue", newValue);
  },
});

const activeQualityCategory = ref(null);

const chordDisplayName = computed(() => {
  return `${chord.value.root}${chord.value.quality}`;
});

const activeQualityOptions = computed(() => {
  if (!activeQualityCategory.value) return [];
  const group = QUALITIES.find((g) => g.label === activeQualityCategory.value);
  return group ? group.options : [];
});

watch(
  () => props.isEditing,
  (isEditing) => {
    if (isEditing && !activeQualityCategory.value) {
      let foundCategory = null;
      if (chord.value.quality !== null) {
        for (const group of QUALITIES) {
          if (group.options.some((opt) => opt.value === chord.value.quality)) {
            foundCategory = group.label;
            break;
          }
        }
      }
      activeQualityCategory.value =
        foundCategory || (QUALITIES.length > 0 ? QUALITIES[0].label : null);
    } else if (!isEditing) {
      activeQualityCategory.value = null;
    }
  }
);

function updateChord(key, value) {
  emit("update:modelValue", { ...chord.value, [key]: value });
}
</script>

<style scoped>
.chord-slot {
  position: relative;
  cursor: grab;
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
.is-playing-halo {
  box-shadow: 0 0 20px 5px rgba(253, 203, 110, 0.7);
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
  gap: 1rem;
  width: 500px;
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
</style>
