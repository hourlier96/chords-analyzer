<template>
  <div class="detailed-analysis-container">
    <div class="analysis-header">
      <h3 class="analysis-grid-title">{{ title }}</h3>
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

        <v-tooltip location="top" text="Dominantes secondaires">
          <template #activator="{ props }">
            <button
              v-bind="props"
              @click="showSecondaryDominants = !showSecondaryDominants"
              class="control-icon-button"
              :class="{ 'is-active': showSecondaryDominants }"
            >
              <span style="font-size: 15px; font-weight: bold">V/</span>
            </button>
          </template>
        </v-tooltip>
      </div>
    </div>
    <div class="analysis-grid">
      <div
        v-for="(item, index) in progressionItems"
        :key="`${title}-${index}`"
        class="chord-progression-group"
        :class="{ 'is-playing-halo': index === currentlyPlayingIndex }"
      >
        <AnalysisCard
          :piano="piano"
          :item="item"
          :analysis="analysis"
          :current-index="index"
          :show-secondary-dominant="showSecondaryDominants"
          :secondary-dominant-chord="secondaryDominantsMap.get(item.chord)"
          :is-substitution="isSubstitution"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import * as Tone from "tone";
import { mdiPlay, mdiStop } from "@mdi/js";

import { sleep } from "@/utils.js";
import AnalysisCard from "@/components/analysis/AnalysisCard.vue";

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  progressionItems: {
    type: Array,
    required: true,
  },
  analysis: {
    type: Object,
    required: true,
  },
  piano: {
    type: Object,
    required: true,
  },
  secondaryDominantsMap: {
    type: Map,
    required: true,
  },
  isSubstitution: {
    type: Boolean,
    default: false,
  },
});

const showSecondaryDominants = ref(false);
const isPlaying = ref(false);
const currentlyPlayingIndex = ref(null);

const playEntireProgression = async () => {
  if (isPlaying.value) return;

  if (Tone.getContext().state !== "running") {
    await Tone.start();
  }

  isPlaying.value = true;

  try {
    for (const [index, item] of props.progressionItems.entries()) {
      if (!isPlaying.value) break;
      if (!item.chord) continue;

      currentlyPlayingIndex.value = index;

      const parseChordString = (chordStr) => {
        const rootMatch = chordStr.match(/^[A-G][#b]?/);
        if (!rootMatch) return null;
        const root = rootMatch[0];
        const quality = chordStr.substring(root.length);
        return {
          root,
          quality,
          inversion: props.analysis.progression[index]?.inversion || 0,
        };
      };

      // La logique de lecture des dominantes secondaires reste ici
      if (showSecondaryDominants.value) {
        const secondary = props.secondaryDominantsMap.get(item.chord);
        if (secondary && secondary != "N/A") {
          const secondaryChordObject = parseChordString(secondary);
          if (secondaryChordObject) {
            props.piano.play(secondaryChordObject);
          }
          await sleep(1000);
        }
      }

      const mainChordObject = parseChordString(item.chord);
      if (mainChordObject) {
        props.piano.play(mainChordObject);
      }
      await sleep(1000);
    }
  } catch (error) {
    console.error("Error during playback:", error);
  } finally {
    isPlaying.value = false;
    currentlyPlayingIndex.value = null;
  }
};

function stopSound() {
  isPlaying.value = false;
  props.piano.releaseAll();
  currentlyPlayingIndex.value = null;
}
</script>

<style scoped>
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
}

.analysis-grid-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.header-controls {
  display: flex;
  gap: 0.5rem;
}

.control-icon-button {
  background-color: #4a4a4a;
  color: #edf2f4;
  border: 1px solid #555;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  padding: 0;
  cursor: pointer;
  transition:
    background-color 0.2s,
    border-color 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
}

.control-icon-button:hover:not(:disabled) {
  background-color: #5a5a5a;
  border-color: #777;
}

.control-icon-button.is-active {
  color: #000000;
  background-color: #6497cc;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 1.5rem;
}

.chord-progression-group {
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 12px;
  transition: box-shadow 0.3s ease-in-out;
}

.chord-progression-group.is-playing-halo {
  box-shadow: 0 0 20px 5px rgba(253, 203, 110, 0.7);
}
</style>
