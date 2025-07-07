<template>
  <main>
    <div>
      <v-dialog v-model="isSettingsOpen" max-width="500">
        <template #activator="{ props: activatorProps }">
          <button
            v-bind="activatorProps"
            class="control-icon-button"
            aria-label="Ouvrir les paramètres"
          >
            <v-icon :icon="mdiCog" />
          </button>
        </template>

        <v-card class="settings-container" width="300px">
          <v-card-title class="text-h5"> Paramètres </v-card-title>
          <v-card-text>
            <div class="setting-item-modal">
              Mode de lecture audio
              <v-tooltip
                location="top"
                :text="
                  playbackMode === 'arpeggio'
                    ? 'Passer en mode accords plaqués'
                    : 'Passer en mode arpège'
                "
              >
                <template #activator="{ props: tooltipProps }">
                  <button
                    v-bind="tooltipProps"
                    @click="
                      setPlaybackMode(
                        playbackMode === 'arpeggio' ? 'chord' : 'arpeggio'
                      )
                    "
                    class="control-icon-button"
                  >
                    <v-icon
                      :icon="
                        playbackMode === 'arpeggio'
                          ? mdiWaveform
                          : mdiMusicCircle
                      "
                    />
                  </button>
                </template>
              </v-tooltip>
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="blue-darken-1"
              text="Fermer"
              @click="isSettingsOpen = false"
            ></v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
    <ChordProgressionBuilder
      v-model="progression"
      :is-loading="isLoading"
      :error="analysisError"
      @analyze="analyzeProgression()"
    />

    <div v-if="analysisStore.hasResult" class="content-grid">
      <div class="left-column">
        <div class="results-box">
          <div class="title-and-controls">
            <h2 class="result-title">
              {{ analysisResults.tonic }}
              {{ analysisResults.mode.replace(" (Original)", "") }}
              <v-tooltip location="right" v-if="analysisResults.explanations">
                <template #activator="{ props }">
                  <v-icon
                    v-bind="props"
                    size="x-small"
                    :icon="mdiInformation"
                  ></v-icon>
                </template>
                <span
                  class="explanation-content"
                  style="max-width: 250px; white-space: normal; display: block"
                  >{{ analysisResults.explanations }}</span
                >
              </v-tooltip>
            </h2>

            <div class="global-controls">
              <div class="mode-button-wrapper">
                <v-tooltip location="top" text="Substitutions modales">
                  <template #activator="{ props: tooltipProps }">
                    <v-menu location="bottom">
                      <template #activator="{ props: menuProps }">
                        <button
                          v-bind="{ ...tooltipProps, ...menuProps }"
                          class="control-icon-button"
                          :class="{ 'is-active': activeMode }"
                        >
                          <v-icon :icon="mdiSync" />
                        </button>
                      </template>
                      <v-list density="compact" class="modal-list">
                        <v-list-item
                          v-for="option in modeOptions"
                          :key="option.value"
                          @click="activeMode = option.value"
                          :class="{ 'is-active': activeMode === option.value }"
                        >
                          <v-list-item-title>{{
                            option.title
                          }}</v-list-item-title>
                        </v-list-item>
                      </v-list>
                    </v-menu>
                  </template>
                </v-tooltip>

                <v-tooltip
                  v-if="activeMode"
                  location="top"
                  text="Réinitialiser"
                >
                  <template #activator="{ props }">
                    <button
                      v-bind="props"
                      @click="resetActiveMode()"
                      class="reset-mode-button"
                    >
                      <v-icon :icon="mdiClose" size="x-small"></v-icon>
                    </button>
                  </template>
                </v-tooltip>
              </div>
            </div>
          </div>
        </div>

        <div class="analysis-grids-container">
          <AnalysisGrid
            v-if="analysisResults.quality_analysis"
            :title="`${analysisResults.tonic} ${analysisResults.mode}`"
            :progression-items="analysisResults.quality_analysis"
            :analysis="analysisStore.lastAnalysis"
            :piano="piano"
            :secondary-dominants-map="secondaryDominantsMap"
          />

          <AnalysisGrid
            v-if="activeMode && substitutedModalProgression.length > 0"
            :title="activeModeTitle"
            :progression-items="substitutedModalProgression"
            :analysis="analysisStore.lastAnalysis"
            :piano="piano"
            :secondary-dominants-map="secondaryDominantsMap"
            :is-substitution="true"
          />
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed } from "vue";
import {
  mdiInformation,
  mdiWaveform,
  mdiMusicCircle,
  mdiCog,
  mdiSync,
  mdiClose,
} from "@mdi/js";

import { useAnalysisStore } from "@/stores/analysis.js";
import { piano, playbackMode, setPlaybackMode } from "@/sampler.js";

import AnalysisGrid from "@/components/analysis/AnalysisGrid.vue";
import ChordProgressionBuilder from "@/components/progression/ChordProgressionBuilder.vue";

const analysisStore = useAnalysisStore();

const isSettingsOpen = ref(false);

const defaultProgression = [
  [
    {
      id: 1,
      root: "D",
      quality: "7",
      inversion: 2,
    },
    {
      id: 2,
      root: "Bb",
      quality: "maj7",
      inversion: 0,
    },
    {
      id: 3,
      root: "C",
      quality: "7",
      inversion: 3,
    },
    {
      id: 4,
      root: "G",
      quality: "7b9",
      inversion: 0,
    },
    {
      id: 5,
      root: "F",
      quality: "maj9",
      inversion: 0,
    },
  ],
];

const progression = ref(
  analysisStore.lastAnalysis.progression &&
    analysisStore.lastAnalysis.progression.length > 0
    ? JSON.parse(JSON.stringify(analysisStore.lastAnalysis.progression))
    : defaultProgression
);

const isLoading = ref(false);
const analysisError = ref(null);

const activeMode = ref(null);
const analysisResults = computed(() => analysisStore.lastAnalysis.result);

const modeOptions = computed(() => {
  if (!analysisResults.value?.major_modes_substitutions) {
    return [];
  }
  return Object.entries(analysisResults.value.major_modes_substitutions).map(
    ([modeName, modeData]) => ({
      title: `${modeName}: ${modeData.borrowed_scale}`,
      value: modeName,
    })
  );
});

const activeModeTitle = computed(() => {
  if (!activeMode.value || !modeOptions.value.length) return "";
  const selectedOption = modeOptions.value.find(
    (opt) => opt.value === activeMode.value
  );
  return selectedOption ? selectedOption.title : "";
});

const substitutedModalProgression = computed(() => {
  if (!analysisResults.value) return [];
  const modeData =
    analysisResults.value.major_modes_substitutions?.[activeMode.value];

  if (!modeData || !modeData.substitution) {
    return [];
  }
  return modeData.substitution.map((item) => {
    return {
      chord: item.chord,
      found_numeral: item.roman,
      found_quality: item.quality,
      is_diatonic: false,
      expected_chord_name: null,
      expected_numeral: null,
    };
  });
});

const secondaryDominantsMap = computed(() => {
  const map = new Map();
  if (analysisResults.value && analysisResults.value.secondary_dominants) {
    const allModesData = Object.values(
      analysisResults.value.secondary_dominants
    );
    for (const dominantPairsForMode of allModesData) {
      for (const dominantPair of dominantPairsForMode) {
        const [secondaryChord, targetChord] = dominantPair;
        map.set(targetChord, secondaryChord);
      }
    }
  }
  return map;
});

function resetActiveMode() {
  activeMode.value = null;
}

const progressionForApi = computed(() => {
  return progression.value.map((chord) => `${chord.root}${chord.quality}`);
});

async function analyzeProgression() {
  isLoading.value = true;
  analysisError.value = null;
  analysisStore.clearResult();

  const chords = progressionForApi.value;
  if (chords.length < 2) {
    analysisError.value =
      "Veuillez construire une progression d'au moins 2 accords.";
    isLoading.value = false;
    return;
  }

  try {
    const response = await fetch("http://localhost:8000/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chords }),
    });
    if (!response.ok)
      throw new Error(`Erreur du serveur: ${response.statusText}`);
    const data = await response.json();
    if (data.error) throw new Error(data.error);

    const progressionSnapshot = JSON.parse(JSON.stringify(progression.value));
    analysisStore.setLastAnalysis(data, progressionSnapshot);
  } catch (e) {
    analysisError.value = `Une erreur est survenue : ${e.message}`;
    analysisStore.clearResult();
  } finally {
    isLoading.value = false;
  }
}
</script>

<style>
/* ==========================================================================
   Styles de Base et Typographie
   ========================================================================== */
:root {
  background-color: #242424;
  color: rgba(255, 255, 255, 0.87);
  color-scheme: light dark;
  font-family:
    -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial,
    sans-serif;
  font-weight: 400;
  line-height: 1.6;
}

h1 {
  font-size: 2.2rem;
  font-weight: 700;
}

h3 {
  border-bottom: 1px solid #444;
  padding-bottom: 0.5rem;
}

/* ==========================================================================
   Mise en page principale
   ========================================================================== */
#app {
  align-items: flex-start;
  box-sizing: border-box;
  display: flex;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
}

main {
  margin: 0;
  max-width: 1200px;
  padding: 2rem;
  width: 100%;
}

header {
  margin-bottom: 2rem;
  text-align: center;
}

/* ==========================================================================
   Conteneurs et Grilles
   ========================================================================== */
.results-box {
  background-color: #2f2f2f;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  padding: 1rem;
}

.analysis-grids-container {
  display: flex;
  flex-direction: row;
  gap: 1.5rem;
}

.analysis-grids-container > * {
  flex: 1;
  min-width: 0;
}

.settings-container {
  background-color: #d6d6d6;
}

.setting-item-modal {
  align-items: center;
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

/* ==========================================================================
   Composants (Boutons, Titres, etc.)
   ========================================================================== */
.result-title {
  color: #a0cfff;
  margin-top: 0;
  font-weight: bold;
  font-size: 40px;
  text-align: center;
}

.explanation-content {
  color: #e8e8e8;
  display: block;
  font-size: 14px;
  line-height: 1.4;
  max-width: 400px;
  padding: 8px 12px;
  text-align: justify;
  white-space: normal;
}

.mode-button-wrapper {
  display: inline-block;
  position: relative;
}

/* --- Styles des boutons --- */
.control-icon-button {
  align-items: center;
  background-color: #4a4a4a;
  border: 1px solid #555;
  border-radius: 50%;
  color: #edf2f4;
  cursor: pointer;
  display: flex;
  font-family: "Courier New", Courier, monospace;
  font-size: 1rem;
  font-weight: bold;
  height: 40px;
  justify-content: center;
  padding: 0;
  transition:
    background-color 0.2s,
    border-color 0.2s;
  width: 40px;
}

.reset-mode-button {
  align-items: center;
  background-color: #d32f2f;
  border: 1px solid #ffffff;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  color: white;
  cursor: pointer;
  display: flex;
  height: 20px;
  justify-content: center;
  padding: 0;
  position: absolute;
  right: -8px;
  top: -8px;
  transition: background-color 0.2s;
  width: 20px;
  z-index: 10;
}

/* ==========================================================================
   Modificateurs et États
   ========================================================================== */
.global-controls .control-icon-button:hover,
.reset-mode-button:hover {
  background-color: #5a5a5a;
  border-color: #777;
}

.reset-mode-button:hover {
  background-color: #e57373;
}

.global-controls .control-icon-button.is-active {
  background-color: #fdcb6e;
  color: #000;
}

.control-icon-button.is-active .v-icon {
  color: #000000;
}

.modal-list .is-active {
  background-color: #6497cc;
}
</style>
