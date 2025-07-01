<script setup>
import { ref, computed } from "vue";
import { useAnalysisStore } from "@/stores/analysis.js";
import { mdiInformation, mdiInformationOff } from "@mdi/js";
import AnalysisGrid from "@/components/AnalysisGrid.vue";
import ChordProgressionBuilder from "@/components/ChordProgressionBuilder.vue";

const analysisStore = useAnalysisStore();

const defaultProgression = [
  { id: 1, root: "A", quality: "m" },
  { id: 2, root: "G", quality: "" },
  { id: 3, root: "C", quality: "" },
];
const progression = ref(
  analysisStore.lastAnalysis.progression &&
    analysisStore.lastAnalysis.progression.length > 0
    ? analysisStore.lastAnalysis.progression
    : defaultProgression
);

const isLoading = ref(false);
const analysisError = ref(null);
const isExplanationVisible = ref(false);

// --- 3. Fonctions (Logique de l'interface et de l'API) ---

const analysisResults = computed(() => {
  return analysisStore.lastAnalysis.result;
});

// Crée la liste d'accords (ex: ["Am", "G", "C"]) pour l'API
const progressionForApi = computed(() => {
  return progression.value.map((chord) => `${chord.root}${chord.quality}`);
});

function toggleExplanation() {
  isExplanationVisible.value = !isExplanationVisible.value;
}

// Fonction principale d'appel à l'API
async function analyzeProgression() {
  isLoading.value = true;
  analysisError.value = null;
  analysisStore.clearResult();
  isExplanationVisible.value = false;

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
            <span v-if="analysisResults.explanations">
              <v-icon
                size="x-small"
                :icon="
                  isExplanationVisible ? mdiInformationOff : mdiInformation
                "
                :aria-label="
                  isExplanationVisible
                    ? 'Masquer l\'explication'
                    : 'Afficher l\'explication'
                "
                @click="toggleExplanation"
              ></v-icon>
            </span>
          </h2>

          <div class="explanation-section">
            <div v-show="isExplanationVisible" class="explanation-content">
              <p>{{ analysisResults.explanations }}</p>
            </div>
          </div>
          <AnalysisGrid
            v-if="analysisResults.quality_analysis"
            :analysis-results="analysisResults"
          />

          <h3 v-if="analysisResults.major_modes_substitutions">
            Table de Substitutions Modales :
          </h3>
          <table
            v-if="analysisResults.major_modes_substitutions"
            class="substitutions-table"
          >
            <thead>
              <tr>
                <th>Mode</th>
                <th>Gamme d'emprunt</th>
                <th>Substitution</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(
                  data, modeName
                ) in analysisResults.major_modes_substitutions"
                :key="modeName"
              >
                <td>
                  <strong>{{ modeName.replace(" (Original)", "") }}</strong>
                  <span
                    v-if="modeName.includes('(Original)')"
                    class="original-tag"
                    >(Original)</span
                  >
                </td>
                <td>{{ data.borrowed_scale }}</td>
                <td class="progression-cell">
                  <span
                    v-for="(chord, index) in data.substitution"
                    :key="index"
                    class="chord"
                  >
                    {{ chord !== null ? chord : "-" }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
          <h3 v-if="analysisResults.harmonized_chords">
            Harmonisation des Accords
          </h3>
          <table
            v-if="analysisResults.harmonized_chords"
            class="substitutions-table"
          >
            <thead>
              <tr>
                <th>Mode</th>
                <th>Harmonisation</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(chords, modeName) in analysisResults.harmonized_chords"
                :key="modeName"
              >
                <td>
                  <strong>{{ modeName.replace(" (Original)", "") }}</strong>
                  <span
                    v-if="modeName.includes('(Original)')"
                    class="original-tag"
                    >(Original)</span
                  >
                </td>
                <td class="progression-cell">
                  <span
                    v-for="(chord, index) in chords"
                    :key="index"
                    class="chord"
                  >
                    {{ chord || "-" }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="right-column">
        <div
          v-if="
            analysisResults.secondary_dominants &&
            analysisResults.secondary_dominants.length > 0
          "
          class="results-box"
        >
          <h3>Dominantes Secondaires</h3>
          <table class="info-table">
            <thead>
              <tr>
                <th>Dominante</th>
                <th>Résolution</th>
                <th>Fonction</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, index) in analysisResults.secondary_dominants"
                :key="index"
              >
                <td>{{ row[0] }}</td>
                <td>{{ row[1] }}</td>
                <td>{{ row[2] }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div
          v-if="
            analysisResults.tritone_substitutions &&
            analysisResults.tritone_substitutions.length > 0
          "
          class="results-box"
        >
          <h3>Substitutions Tritoniques</h3>
          <table class="info-table">
            <thead>
              <tr>
                <th>Accord</th>
                <th>Triton</th>
                <th>Notes communes</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, index) in analysisResults.tritone_substitutions"
                :key="index"
              >
                <td>{{ row[0] }}</td>
                <td>{{ row[1] || "-" }}</td>
                <td>{{ row[2] || "-" }}</td>
              </tr>
            </tbody>
          </table>
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
.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  margin-top: 2rem;
  align-items: flex-start;
}
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
.explanation-section {
  margin-top: 1.5rem;
  margin-bottom: 1rem;
}
.explanation-toggle {
  background: none;
  border: none;
  color: #00aaff;
  text-decoration: underline;
  cursor: pointer;
  padding: 0;
  font-size: 1rem;
}
.explanation-toggle:hover {
  color: #00cfff;
}
.explanation-content {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #3a3a3a;
  border-left: 3px solid #00aaff;
  border-radius: 4px;
  color: #ddd;
  text-align: justify;
}
.explanation-content p {
  margin: 0;
}
.borrowed-item {
  background-color: #3c3c3c;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.9em;
  margin-top: 0.5rem;
}

/* Styles pour les tableaux */
.substitutions-table,
.info-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}
.substitutions-table th,
.substitutions-table td,
.info-table th,
.info-table td {
  border: 1px solid #444;
  padding: 0.8rem;
  text-align: left;
  vertical-align: middle;
}
.substitutions-table th,
.info-table th {
  background-color: #4a4a4a;
}
.original-tag {
  font-size: 0.8em;
  font-style: italic;
  color: #00bcd4;
  margin-left: 0.5rem;
}
.progression-cell {
  font-family: "Courier New", Courier, monospace;
  display: flex;
  justify-content: flex-start;
  gap: 1rem;
  flex-wrap: wrap;
}
.chord {
  display: inline-block;
  min-width: 55px;
  text-align: left;
}
</style>
