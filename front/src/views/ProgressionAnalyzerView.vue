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

          <AnalysisGrid
            v-if="analysisResults.quality_analysis"
            :analysis="analysisStore.lastAnalysis"
            :piano="piano"
          />
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed } from "vue";
import { mdiInformation, mdiWaveform, mdiMusicCircle, mdiCog } from "@mdi/js";

import { useAnalysisStore } from "@/stores/analysis.js";
import { piano, playbackMode, setPlaybackMode } from "@/sampler.js";

import AnalysisGrid from "@/components/analysis/AnalysisGrid.vue";
import ChordProgressionBuilder from "@/components/progression/ChordProgressionBuilder.vue";

const analysisStore = useAnalysisStore();

const isSettingsOpen = ref(false);

const defaultProgression = [
  { id: 1, root: "C", quality: "", inversion: 0 },
  { id: 2, root: "D", quality: "m7", inversion: 0 },
  { id: 3, root: "G", quality: "7", inversion: 0 },
  { id: 4, root: "F", quality: "maj7", inversion: 0 },
  { id: 5, root: "A", quality: "m7", inversion: 0 },
  { id: 6, root: "D", quality: "7", inversion: 0 },
  { id: 7, root: "D", quality: "7", inversion: 1 },
  { id: 8, root: "G", quality: "", inversion: 1 },
];

const progression = ref(
  analysisStore.lastAnalysis.progression &&
    analysisStore.lastAnalysis.progression.length > 0
    ? JSON.parse(JSON.stringify(analysisStore.lastAnalysis.progression))
    : defaultProgression
);

const isLoading = ref(false);
const analysisError = ref(null);

const analysisResults = computed(() => {
  return analysisStore.lastAnalysis.result;
});

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
:root {
  font-family:
    -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial,
    sans-serif;
  line-height: 1.6;
  font-weight: 400;
  color-scheme: light dark;
  color: rgba(255, 255, 255, 0.87);
  background-color: #242424;
}
#app {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  padding: 2rem;
  box-sizing: border-box;
}
main {
  max-width: 1200px;
  width: 100%;
  margin: 0;
  padding: 2rem;
}
header {
  text-align: center;
  margin-bottom: 2rem;
}
h1 {
  font-size: 2.2rem;
  font-weight: 700;
}
h3 {
  border-bottom: 1px solid #444;
  padding-bottom: 0.5rem;
}

.settings-container {
  background-color: #d6d6d6;
}

.setting-item-modal {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.control-icon-button {
  background-color: #4a4a4a;
  color: #edf2f4;
  border: 1px solid #555;
  border-radius: 50%;
  margin-bottom: 5px;
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

/* Styles pour la grille de résultats */
.results-box {
  background-color: #2f2f2f;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}
.result-title {
  text-align: center;
  font-family: "Courier New", Courier, monospace;
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #a0cfff;
}

.explanation-content {
  max-width: 400px;
  white-space: normal;
  display: block;
  padding: 8px 12px;
  font-size: 14px;
  color: #e8e8e8;
  line-height: 1.4;
  text-align: justify;
}
</style>
