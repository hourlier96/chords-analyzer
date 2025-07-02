<script setup>
import { ref, computed } from "vue";
import { useAnalysisStore } from "@/stores/analysis.js";
import { mdiInformation } from "@mdi/js";
import AnalysisGrid from "@/components/AnalysisGrid.vue";
import ChordProgressionBuilder from "@/components/ChordProgressionBuilder.vue";

const analysisStore = useAnalysisStore();

const defaultProgression = [
  { id: 1, root: "A", quality: "m" },
  { id: 2, root: "D", quality: "7" },
  { id: 3, root: "G", quality: "7" },
  { id: 4, root: "C", quality: "" },
  { id: 5, root: "F", quality: "maj7" },
  { id: 5, root: "F", quality: "m" },
  { id: 5, root: "C", quality: "" },
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

<template>
  <main>
    <header>
      <h1>Analyseur de Progressions Modales</h1>
      <p>
        Construisez votre progression d'accords ci-dessous, puis lancez
        l'analyse.
      </p>
    </header>

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
          />
        </div>
      </div>
    </div>
  </main>
</template>

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

.explanation-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 38px; /* Assure une taille minimale au bouton */
  min-height: 38px;
}

.info-icon {
  width: 1.5em; /* Taille de l'icône relative à la police */
  height: 1.5em;
  color: rgb(96, 170, 239);
}

/* Styles pour les sections d'analyse */
.roman-analysis {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 0.5rem 1rem;
  font-family: "Courier New", Courier, monospace;
  background-color: #3a3a3a;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 2rem;
  align-items: center;
}
.roman-analysis span:nth-child(odd) {
  font-weight: 600;
  color: #a0cfff;
  text-align: right;
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
.borrowed-item {
  background-color: #3c3c3c;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.9em;
  margin-top: 0.5rem;
}
</style>
