<template>
  <div class="detailed-analysis-container">
    <div class="analysis-header">
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
      </div>
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
        v-for="(item, index) in displayedProgression"
        :key="`${selectedMode || 'original'}-${index}`"
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
import { ref, computed } from "vue";
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

// État pour le mode sélectionné, initialisé avec le nom du mode de la prop 'title'
const selectedMode = ref(null);

// Extrait la note racine (ex: "A#") du titre
const rootNote = computed(() => props.title.split(" ")[0]);

// Liste des modes disponibles pour le dropdown
const availableModes = computed(() =>
  Object.keys(props.analysis.result.harmonized_chords)
);

// Propriété calculée qui génère la progression à afficher
const displayedProgression = computed(() => {
  // Si aucun mode n'est sélectionné, retourne la progression d'origine
  if (!selectedMode.value) {
    return props.progressionItems;
  }

  const newModeChords =
    props.analysis.result.harmonized_chords[selectedMode.value];
  const originalModeName = props.title.split(" ")[1];
  const originalModeChords =
    props.analysis.result.harmonized_chords[originalModeName];

  if (!newModeChords || !originalModeChords) {
    return props.progressionItems;
  }

  return props.progressionItems.map((item, index) => {
    const isOriginallyDiatonic = originalModeChords[index] !== null;
    const newChord = newModeChords[index];

    if (isOriginallyDiatonic && newChord) {
      return {
        ...item,
        chord: newChord,
      };
    } else {
      return item;
    }
  });
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
    for (const [index, item] of displayedProgression.value.entries()) {
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

      if (showSecondaryDominants.value) {
        const secondary = props.secondaryDominantsMap.get(item.chord);
        if (secondary && secondary != "N/A") {
          const secondaryChordObject = parseChordString(secondary);
          if (secondaryChordObject) {
            props.piano.play(secondaryChordObject);
            await sleep(1000);
          }
        }
      }

      const mainChordObject = parseChordString(item.chord);
      if (mainChordObject) {
        props.piano.play(mainChordObject);
        await sleep(1000);
      }
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
  gap: 1rem;
}

.mode-selector-wrapper {
  flex-grow: 1;
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
  transition: border-color 0.2s;
}

.mode-selector:hover {
  border-color: #777;
}

.mode-selector:focus {
  outline: none;
  border-color: #6497cc;
}

.header-controls {
  display: flex;
  gap: 0.5rem;
}

.legend {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 13px;
  color: #bdc3c7;
  flex-shrink: 0;
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
