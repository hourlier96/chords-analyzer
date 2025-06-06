<template>
  <div class="detailed-analysis-container">
    <div class="analysis-header">
      <div class="left-controls">
        <PlayerControls
          :is-playing="isPlaying"
          v-model:time-signature="timeSignature"
          v-model:is-metronome-active="isMetronomeActive"
          v-model:is-looping="isLooping"
          @play="playEntireProgression"
          @stop="stopSound"
        />

        <v-tooltip location="top" text="Dominantes secondaires"> </v-tooltip>
      </div>
    </div>

    <div class="progression-grid-container">
      <div class="substitution-header">
        <div v-if="!isSubstitution" class="mode-selector-wrapper">
          <select v-model="selectedMode" class="mode-selector">
            <option :value="null">Progression d'origine ({{ title }})</option>
            <option v-for="mode in availableModes" :key="mode" :value="mode">
              {{ rootNote }} {{ mode }}
            </option>
          </select>
        </div>
        <div v-else>
          <h3 class="analysis-grid-title">{{ title }}</h3>
        </div>

        <div v-if="!isSubstitution" class="legend">
          <div class="legend-item">
            <div class="legend-dot" style="background-color: #2ecc71"></div>
            <span>Diatonique</span>
          </div>
          <div class="legend-item">
            <div class="legend-dot" style="background-color: #f1c40f"></div>
            <span>Emprunts</span>
          </div>
          <div class="legend-item">
            <div class="legend-square" style="background-color: #304e75"></div>
            <span>Non substituable</span>
          </div>
        </div>
      </div>
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
        <div
          v-for="(item, index) in displayedProgression"
          :key="item.id"
          class="chord-wrapper"
          :style="{
            gridColumn: `${item.start} / span ${item.duration}`,
          }"
          :class="{ 'is-playing-halo': index === currentlyPlayingIndex }"
        >
          <AnalysisCard
            :piano="piano"
            :item="item"
            :analysis="analysis"
            :show-secondary-dominant="showSecondaryDominants"
            :secondary-dominant-chord="secondaryDominantsMap.get(item.chord)"
            :is-substitution="isSubstitution"
            :beat-width="BEAT_WIDTH"
            @update:item="(newItem) => updateProgressionItem(index, newItem)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";

import { BEAT_WIDTH, useStatePlayer } from "@/composables/useStatePlayer.js";
import { sleep } from "@/utils.js";
import { useTempoStore } from "@/stores/tempo.js";
import AnalysisCard from "@/components/analysis/AnalysisCard.vue";
import TimelineGrid from "@/components/common/TimelineGrid.vue";
import PlayerControls from "@/components/common/PlayerControls.vue";

const props = defineProps({
  title: { type: String, required: true },
  progressionItems: { type: Array, required: true },
  analysis: { type: Object, required: true },
  piano: { type: Object, required: true },
  secondaryDominantsMap: { type: Map, required: true },
  isSubstitution: { type: Boolean, default: false },
});

const emit = defineEmits(["update:progressionItems"]);

const tempoStore = useTempoStore();
const selectedMode = ref(null);
const showSecondaryDominants = ref(false);
const progressionState = ref([]);

watch(
  () => props.progressionItems,
  (newItems) => {
    progressionState.value = newItems.map((item) => ({
      ...item,
      duration: item.duration || 2,
      inversion: item.inversion || 0,
    }));
  },
  { immediate: true, deep: true }
);

const rootNote = computed(() => props.title.split(" ")[0]);
const availableModes = computed(() =>
  Object.keys(props.analysis.result.harmonized_chords)
);

const displayedProgression = computed(() => {
  let baseProgression = progressionState.value;

  if (selectedMode.value) {
    const newModeChords =
      props.analysis.result.harmonized_chords[selectedMode.value];
    const titleParts = props.title.split(" ");
    const originalModeName = titleParts.slice(1).join(" ");
    const originalModeChords =
      props.analysis.result.harmonized_chords[originalModeName];
    if (newModeChords && originalModeChords) {
      baseProgression = progressionState.value.map((item, index) => {
        const isOriginallyDiatonic = originalModeChords[index] !== null;
        const newChordData = newModeChords[index];

        if (isOriginallyDiatonic && newChordData) {
          return {
            ...item,
            ...newChordData,
          };
        }
        return item;
      });
    }
  }

  let currentBeat = 1;
  return baseProgression.map((chord) => {
    const start = currentBeat;
    currentBeat += chord.duration;
    return { ...chord, start };
  });
});

function updateProgressionItem(index, newItem) {
  const newProgression = [...progressionState.value];
  const cleanItem = { ...newItem };
  delete cleanItem.start;
  newProgression[index] = cleanItem;
  progressionState.value = newProgression;
  emit("update:progressionItems", newProgression);
}

const parseChordString = (chordStr, inversion = 0) => {
  if (!chordStr) return null;
  const rootMatch = chordStr.match(/^[A-G][#b]?/);
  if (!rootMatch) return null;
  const root = rootMatch[0];
  const quality = chordStr.substring(root.length);
  return { root, quality, inversion: inversion };
};

const handlePlayItemAnalysis = async ({ item }) => {
  if (!item.chord) return;

  const mainChordObject = parseChordString(item.chord, item.inversion);
  let chordDurationMs = item.duration * tempoStore.beatDurationMs;

  if (showSecondaryDominants.value) {
    const secondary = props.secondaryDominantsMap.get(item.chord);
    if (secondary && secondary !== "N/A") {
      const secondaryChordObject = parseChordString(secondary);
      if (secondaryChordObject) {
        const secondaryDurationMs = Math.min(
          chordDurationMs,
          tempoStore.beatDurationMs
        );
        props.piano.play(secondaryChordObject);
        await sleep(secondaryDurationMs);
        chordDurationMs -= secondaryDurationMs;
      }
    }
  }

  if (mainChordObject && chordDurationMs > 0) {
    props.piano.play(mainChordObject);
    await sleep(chordDurationMs);
  }
};

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
} = useStatePlayer(displayedProgression, {
  onPlayItemAsync: handlePlayItemAnalysis,
});
</script>

<style scoped>
/* Les styles restent inchangés */
.detailed-analysis-container {
  background-color: #3a3a3a;
  border-radius: 8px;
  padding: 1rem;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding: 0 0.5rem;
  border-bottom: 1px solid #4f4f4f;
  padding-bottom: 0.8rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.mode-selector-wrapper {
  flex-shrink: 0;
  min-width: 180px;
}
.mode-selector {
  background-color: #4a4a4a;
  color: #edf2f4;
  border: 1px solid #555;
  border-radius: 6px;
  padding: 0.5rem 0.8rem;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  width: 100%;
}
.mode-selector:hover {
  border-color: #777;
}
.mode-selector:focus {
  outline: none;
  border-color: #6497cc;
}
.legend {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 13px;
  color: #bdc3c7;
  flex-shrink: 0;
  flex-grow: 1;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.legend-square {
  width: 30px;
  height: 10px;
}
.substitution-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
  margin-bottom: 0.5rem;
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
  background-color: #6497cc;
  color: #000;
  border-color: #5078a0;
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

.progression-grid-container {
  overflow-x: auto;
  padding: 5px;
  background-color: #2c2c2c;
  border: 1px solid #444;
  border-radius: 8px;
}

.chords-track {
  display: grid;
  grid-template-columns: repeat(var(--total-beats, 8), var(--beat-width));
  grid-auto-rows: minmax(100px, auto);
  align-items: stretch;
}

.chord-wrapper {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: box-shadow 0.3s ease-in-out;
  border-radius: 12px;
}

.is-playing-halo .analysis-card {
  box-shadow: 0 0 20px 5px rgba(253, 203, 110, 0.7);
  border-radius: 12px;
}
</style>
