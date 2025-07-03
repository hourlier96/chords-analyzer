<template>
  <div
    v-if="analysis.result && analysis.result.quality_analysis"
    class="detailed-analysis-container"
  >
    <div class="analysis-header">
      <div class="header-controls">
        <v-tooltip location="top" text="Lire la progression">
          <template #activator="{ props }">
            <button
              v-bind="props"
              @click="playEntireProgression"
              class="control-icon-button"
              :disabled="isPlaying"
            >
              <v-icon :icon="mdiPlay" />
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

        <v-tooltip location="top" text="Substitutions tritoniques pertinentes">
          <template #activator="{ props }">
            <button
              v-bind="props"
              @click="showTritonSubstitutions = !showTritonSubstitutions"
              class="control-icon-button"
              :class="{ 'is-active': showTritonSubstitutions }"
            >
              <v-icon :icon="mdiYinYang" />
            </button>
          </template>
        </v-tooltip>

        <v-tooltip location="top" text="Substitutions modales">
          <template #activator="{ props: tooltipProps }">
            <v-menu location="bottom">
              <template #activator="{ props: menuProps }">
                <button
                  v-bind="{ ...tooltipProps, ...menuProps }"
                  class="control-icon-button"
                  :class="{ 'is-active': activeMode !== 'Ionian (Original)' }"
                >
                  <v-icon :icon="mdiSync" />
                </button>
              </template>
              <v-list density="compact">
                <v-list-item
                  v-for="option in modeOptions"
                  :key="option.value"
                  @click="activeMode = option.value"
                >
                  <v-list-item-title>{{ option.title }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </template>
        </v-tooltip>
      </div>
    </div>

    <div class="analysis-grid">
      <div
        v-for="(item, index) in displayedProgression"
        :key="`${activeMode}-${index}`"
        class="chord-progression-group"
      >
        <AnalysisCard
          :piano="props.piano"
          :item="item"
          :analysis="analysis"
          :current-index="index"
          :is-tritone-mode-active="showTritonSubstitutions"
          :show-secondary-dominant="showSecondaryDominants"
          :secondary-dominant-chord="secondaryDominantsMap.get(item.chord)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import * as Tone from "tone";
import AnalysisCard from "@/components/analysis/AnalysisCard.vue";
import { mdiYinYang, mdiSync, mdiPlay } from "@mdi/js";

const props = defineProps({
  analysis: {
    type: Object,
    required: true,
  },
  piano: { type: Object, required: true },
});

const showSecondaryDominants = ref(false);
const showTritonSubstitutions = ref(false);
const activeMode = ref("Ionian (Original)");
const isPlaying = ref(false);

const modeOptions = computed(() => {
  if (!props.analysis.result?.major_modes_substitutions) {
    return [];
  }
  return Object.entries(props.analysis.result.major_modes_substitutions).map(
    ([modeName, modeData]) => ({
      title: `${modeName}: ${modeData.borrowed_scale}`,
      value: modeName,
    })
  );
});

const displayedProgression = computed(() => {
  if (!props.analysis.result) return [];
  const originalProgression = props.analysis.result.quality_analysis;
  if (activeMode.value === "Ionian (Original)" || !activeMode.value) {
    return originalProgression;
  }
  const modeData =
    props.analysis.result.major_modes_substitutions?.[activeMode.value];
  if (!modeData || !modeData.substitution) {
    return originalProgression;
  }
  return modeData.substitution.map((chordName, index) => {
    // Pour le premier accord (index 0), on retourne l'accord de la progression originale.
    if (index === 0) {
      return originalProgression[0];
    }

    // Pour tous les autres accords, on retourne la substitution.
    return {
      chord: chordName,
      found_numeral: null,
      is_diatonic: false,
      expected_chord_name: null,
      expected_numeral: null,
    };
  });
});

const secondaryDominantsMap = computed(() => {
  const map = new Map();
  if (props.analysis.result && props.analysis.result.secondary_dominants) {
    for (const dominantPair of Object.values(
      props.analysis.result.secondary_dominants
    )) {
      const [secondaryChord, targetChord] = dominantPair;
      map.set(targetChord, secondaryChord);
    }
  }
  return map;
});

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const playEntireProgression = async () => {
  if (isPlaying.value) return;

  if (Tone.getContext().state !== "running") {
    await Tone.start();
  }

  isPlaying.value = true;

  try {
    for (const item of displayedProgression.value) {
      if (!item.chord) continue;

      const parseChordString = (chordStr) => {
        const rootMatch = chordStr.match(/^[A-G][#b]?/);
        if (!rootMatch) return null;
        const root = rootMatch[0];
        const quality = chordStr.substring(root.length);
        return { root, quality };
      };

      if (showSecondaryDominants.value) {
        const secondary = secondaryDominantsMap.value.get(item.chord);
        if (secondary) {
          const secondaryChordObject = parseChordString(secondary);
          if (secondaryChordObject) {
            props.piano.play(secondaryChordObject);
          }
          await sleep(800);
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
  }
};
</script>

<style scoped>
.detailed-analysis-container {
  margin-bottom: 2rem;
}

.analysis-header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 1rem;
  padding: 0 1rem;
}

.header-controls {
  display: flex;
  gap: 0.5rem;
}

.header-controls button {
  background-color: #4a4a4a;
  color: #edf2f4;
  border: 1px solid #555;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  font-weight: bold;
  cursor: pointer;
  transition:
    background-color 0.2s,
    border-color 0.2s,
    opacity 0.2s;
}

.header-controls button:hover {
  background-color: #5a5a5a;
  border-color: #777;
}

.header-controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #4a4a4a;
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

.mode-select {
  max-width: 220px;
  background-color: #4a4a4a;
  color: #edf2f4;
  border-radius: 6px;
}

:deep(.mode-select .v-field) {
  background-color: transparent !important;
  box-shadow: none !important;
}

:deep(.mode-select .v-field__input) {
  padding-top: 2px;
}

.control-icon-button.is-active {
  color: #000000;
  background-color: #6497cc;
}

.control-icon-button.is-active .v-icon {
  color: #000000;
}
button.control-icon-button:has(.v-icon) {
  font-size: 1.2rem;
}
.control-icon-button.is-active:has(.v-icon) {
  background-color: #fdcb6e;
}

.analysis-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  padding: 1rem;
  background-color: #3a3a3a;
  border-radius: 8px;
}

@media (min-width: 600px) {
  .analysis-grid {
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  }
}

.chord-progression-group {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
