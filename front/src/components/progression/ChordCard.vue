<template>
  <div ref="chordSlotRef" class="chord-slot" :style="{ width: cardWidth }">
    <button class="chord-button" @click="$emit('start-editing')">
      {{ chordDisplayName }}
      <div
        v-if="settingsStore.showNotes"
        style="font-size: 18px; font-style: italic"
      >
        {{
          getNotesForChord(chord)
            .map((note) => note.replace(/[0-9]/g, ""))
            .join(" - ")
        }}
      </div>
    </button>

    <button class="remove-button" @click="$emit('remove')">×</button>

    <div v-if="isEditing" class="editor-popover">
      <div class="editor-content">
        <div class="root-note-selector">
          <template v-for="note in NOTES" :key="note">
            <div v-if="note.includes(' / ')" class="enharmonic-pair">
              <button
                v-for="enharmonicNote in note.split(' / ')"
                :key="enharmonicNote"
                @click="updateChord('root', enharmonicNote)"
                :class="{ active: isNoteActive(enharmonicNote) }"
                class="note-button"
              >
                {{ enharmonicNote }}
              </button>
            </div>

            <button
              v-else
              @click="updateChord('root', note)"
              :class="{ active: isNoteActive(note) }"
              class="note-button"
            >
              {{ note }}
            </button>
          </template>
        </div>
        <div class="main-content">
          <div class="quality-selector">
            <div class="category-tabs">
              <button
                v-for="group in QUALITIES"
                :key="group.label"
                @click="activeQualityCategory = group.label"
                :class="{ active: activeQualityCategory === group.label }"
                class="category-tab"
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
                class="option-button"
              >
                {{ option.text }}
              </button>
            </div>
          </div>
          <div class="inversion-control-footer">
            <button
              @click="changeInversion(-1)"
              class="inversion-button"
              :disabled="chord.inversion === 0"
            >
              -
            </button>
            <span>Position {{ chord.inversion + 1 }}</span>
            <button
              @click="changeInversion(1)"
              class="inversion-button"
              :disabled="chord.inversion === 3"
            >
              +
            </button>
          </div>
        </div>
      </div>
      <button @click="$emit('stop-editing')" class="close-editor">OK</button>
    </div>

    <div
      v-if="!isEditing"
      class="resize-handle"
      @mousedown.prevent="startResize"
    ></div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { QUALITIES, NOTES } from "@/constants.js";
import { getNotesForChord } from "@/sampler.js";
import { useSettingsStore } from "@/stores/settings.js";

const settingsStore = useSettingsStore();

const props = defineProps({
  modelValue: { type: Object, required: true },
  isEditing: { type: Boolean, default: false },
  beatWidth: { type: Number, required: true },
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

// --- Le reste de votre script existant reste inchangé ---
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
    if (isEditing) {
      let foundCategory = null;
      if (chord.value.quality) {
        for (const group of QUALITIES) {
          if (group.options.some((opt) => opt.value === chord.value.quality)) {
            foundCategory = group.label;
            break;
          }
        }
      }
      activeQualityCategory.value = foundCategory || "Majeurs";
    } else {
      activeQualityCategory.value = null;
    }
  },
  { immediate: true }
);
function isNoteActive(note) {
  return chord.value.root === getNoteValue(note);
}
function changeInversion(direction) {
  const noteCount = getNotesForChord(chord.value).length;
  const maxInversion = noteCount > 0 ? noteCount - 1 : 0;
  const currentInversion = chord.value.inversion || 0;
  const newInversion = currentInversion + direction;
  if (newInversion >= 0 && newInversion <= maxInversion) {
    updateChord("inversion", newInversion);
  }
}
function updateChord(key, value) {
  emit("update:modelValue", { ...chord.value, [key]: value });
}
function getNoteValue(note) {
  return note.split(" / ")[0];
}

// Propriété calculée pour la largeur de la carte.
const cardWidth = computed(() => {
  const duration = props.modelValue.duration || 4;
  // Utilise la prop au lieu de la constante
  return `${duration * props.beatWidth}px`;
});

// Refs pour suivre l'état du redimensionnement
const initialMouseX = ref(0);
const initialDuration = ref(0);

/**
 * Démarre le processus de redimensionnement au clic sur la poignée.
 */
function startResize(event) {
  initialMouseX.value = event.clientX;
  initialDuration.value = props.modelValue.duration || 4;

  // Ajoute des écouteurs sur toute la fenêtre pour un glissement fluide
  window.addEventListener("mousemove", doResize);
  window.addEventListener("mouseup", stopResize);
}

/**
 * Calcule et applique le redimensionnement pendant le mouvement de la souris.
 */
function doResize(event) {
  const deltaX = event.clientX - initialMouseX.value;
  // Utilise la prop pour le calcul
  const durationChange = Math.round(deltaX / props.beatWidth);

  let newDuration = initialDuration.value + durationChange;
  newDuration = Math.max(1, newDuration);

  if (newDuration !== props.modelValue.duration) {
    emit("update:modelValue", {
      ...props.modelValue,
      duration: newDuration,
    });
  }
}
/**
 * Termine le processus de redimensionnement et nettoie les écouteurs.
 */
function stopResize() {
  window.removeEventListener("mousemove", doResize);
  window.removeEventListener("mouseup", stopResize);
}
</script>

<style scoped>
/* NOUVEAU : Modifications sur le conteneur principal */
.chord-slot {
  position: relative;
  cursor: grab;
  /* La largeur minimale correspond à la largeur d'un temps */
  min-width: 60px;
  /* Petite transition pour un redimensionnement plus doux */
  transition: width 0.1s ease-out;
}
.chord-button {
  padding: 1rem 0;
  font-size: 17px;
  font-weight: 600;
  border-radius: 8px;
  border: 2px solid #555;
  background-color: #3c3c3c;
  color: white;
  /* NOUVEAU : La largeur s'adapte maintenant à son parent */
  width: 100%;
  height: 100%;
  transition: all 0.2s;
}
.chord-button:hover {
  border-color: #007bff;
}
.remove-button {
  position: absolute;
  top: -10px;
  left: -5px;
  width: 15px;
  height: 15px;
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

/* --- Le reste de vos styles reste inchangé --- */

/* --- Fenêtre Pop-over --- */
.editor-popover {
  position: absolute;
  top: calc(100% + 10px);
  left: 50%;
  transform: translateX(-50%);
  border: 1px solid #555555;
  width: 640px;
  background-color: #2c2c2e;
  color: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  z-index: 10;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* --- NOUVEAU : Style pour la poignée de redimensionnement --- */
.resize-handle {
  position: absolute;
  right: -1px;
  top: 0;
  bottom: 0;
  width: 10px;
  cursor: ew-resize;
  z-index: 5;
  border-radius: 4px;
  border-right: 3px solid #ffffff;
  opacity: 0.5;
  transition: opacity 0.2s;
}
.resize-handle:hover {
  opacity: 1;
}

/* --- (Collez le reste de vos styles ici) --- */
.editor-content {
  display: flex;
  flex-direction: row; /* Garde la disposition en 2 colonnes */
  max-height: 270px; /* Hauteur maximale du contenu éditable */
}

/* --- Colonne de gauche (Notes) --- */
.root-note-selector {
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  border-right: 1px solid #444;
  padding: 5px;
  flex-shrink: 0;
}
.note-button {
  background: none;
  border: none;
  color: #a9a9b0;
  padding: 5px 10px;
  cursor: pointer;
  text-align: center;
  font-size: 1rem;
  border-radius: 6px;
  transition:
    background-color 0.2s,
    color 0.2s;
}
.note-button:hover {
  background-color: #3a3a3c;
}
.note-button.active {
  background-color: #0a84ff;
  color: white;
  font-weight: bold;
}

.main-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* --- Section des qualités d'accords --- */
.quality-selector {
  flex-grow: 1;
  padding: 10px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
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
  grid-template-columns: repeat(auto-fill, minmax(85px, 1fr));
  gap: 0.5rem;
  overflow-y: auto;
  padding: 0.25rem;
}
.options-grid button {
  width: 100%; /* S'adapte à la grille */
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

/* --- Footer des renversements (Styles corrigés pour le thème sombre) --- */
.inversion-control-footer {
  flex-shrink: 0; /* Empêche le footer de se réduire */
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-top: 1px solid #444; /* Bordure plus adaptée au thème */
  background-color: #2c2c2e;
}
.inversion-control-footer span {
  font-weight: 500;
  color: #d1d1d6; /* Texte clair visible sur fond sombre */
}
.inversion-button {
  font-family: monospace;
  font-size: 1.5rem;
  font-weight: bold;
  line-height: 1;
  padding: 5px 15px;
  border-radius: 8px;
  border: 1px solid #5f5f5f;
  background-color: #4a4a4a; /* Fond adapté */
  color: white; /* Texte blanc */
  cursor: pointer;
  transition: background-color 0.2s;
}
.inversion-button:hover {
  background-color: #5f5f5f;
}
.inversion-button:active {
  background-color: #3a3a3c;
}

/* --- Bouton de fermeture "OK" --- */
.close-editor {
  padding: 12px;
  background-color: #0a84ff;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  transition: background-color 0.2s;
}
.close-editor:hover {
  background-color: #0073e6;
}
</style>
