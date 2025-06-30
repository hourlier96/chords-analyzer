<script setup>
import { ref, computed } from "vue";
import { useAnalysisStore } from "@/stores/analysis.js";

// --- 1. Définition des données de base pour l'interface ---
const NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
const QUALITIES = [
  { value: "", text: "Majeur" },
  { value: "m", text: "Mineur" },
  { value: "7", text: "Dominant 7" },
  { value: "maj7", text: "Majeur 7" },
  { value: "m7", text: "Mineur 7" },
  { value: "dim", text: "Diminué" },
  { value: "m7b5", text: "Demi-diminué (ø7)" },
  { value: "aug", text: "Augmenté (+)" },
];

const CORE_QUALITIES = {
  maj7: "major",
  M: "major",
  "": "major",
  maj: "major",
  7: "major",
  m7: "minor",
  m: "minor",
  min: "minor",
  m7b5: "diminished",
  dim7: "diminished",
  d: "diminished",
  dim: "diminished",
  aug: "augmented",
};

// --- 2. État réactif de l'application ---

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

const flippedCards = ref(new Set());

let nextChordId =
  progression.value.length > 0
    ? Math.max(...progression.value.map((c) => c.id)) + 1
    : 1;

const editingChordId = ref(null);
const isLoading = ref(false);
const error = ref(null);
const isExplanationVisible = ref(false);

// --- 3. Fonctions (Logique de l'interface et de l'API) ---

const analysisResults = computed(() => {
  return analysisStore.lastAnalysis.result;
});

// Crée la liste d'accords (ex: ["Am", "G", "C"]) pour l'API
const progressionForApi = computed(() => {
  return progression.value.map((chord) => `${chord.root}${chord.quality}`);
});

const isProgressionUnchanged = computed(() => {
  if (!analysisStore.lastAnalysis.progression || !analysisStore.hasResult) {
    return false;
  }
  return (
    JSON.stringify(progression.value) ===
    JSON.stringify(analysisStore.lastAnalysis.progression)
  );
});

function getChordDisplayName(chord) {
  const qualityInfo = QUALITIES.find((q) => q.value === chord.quality);
  return qualityInfo?.text === "Majeur"
    ? chord.root
    : `${chord.root}${chord.quality}`;
}

function addChord() {
  const newId = nextChordId++;
  progression.value.push({ id: newId, root: "C", quality: "" });
  editingChordId.value = newId;
}

function removeChord(idToRemove) {
  progression.value = progression.value.filter((c) => c.id !== idToRemove);
}

function startEditing(chordId) {
  editingChordId.value = editingChordId.value === chordId ? null : chordId;
}

function shouldShowExpected(analysisItem) {
  const { found_quality, expected_quality, found_numeral, expected_numeral } =
    analysisItem;

  if (found_numeral === expected_numeral) return false;

  if (expected_numeral == "N/A") return false;

  const core_found = CORE_QUALITIES[found_quality];
  const core_expected = CORE_QUALITIES[expected_quality];
  if (core_found !== core_expected) return true;

  const TRIAD_QUALITIES = ["", "maj", "M", "m", "min"];
  if (TRIAD_QUALITIES.includes(found_quality)) {
    return false;
  }

  // Règle 4 (par défaut): Pour toute autre différence (ex: 7 vs maj7), on l'affiche.
  return true;
}

function toggleCardFlip(index) {
  if (flippedCards.value.has(index)) {
    flippedCards.value.delete(index); // Si elle est retournée, on la remet à l'endroit
  } else {
    flippedCards.value.add(index); // Sinon, on la retourne
  }
}

function toggleExplanation() {
  isExplanationVisible.value = !isExplanationVisible.value;
}

// Fonction principale d'appel à l'API
async function analyzeProgression() {
  isLoading.value = true;
  error.value = null;
  analysisStore.clearResult();
  isExplanationVisible.value = false;

  const chords = progressionForApi.value;
  if (chords.length < 2) {
    error.value = "Veuillez construire une progression d'au moins 2 accords.";
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
    error.value = `Une erreur est survenue : ${e.message}`;
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

    <div class="builder-area">
      <div class="progression-builder">
        <div
          v-for="chord in progression"
          :key="chord.id"
          class="chord-slot"
          :ref="
            (el) => {
              if (chord.id === editingChordId) activeChordSlotRef = el;
            }
          "
        >
          <button class="chord-button" @click="startEditing(chord.id)">
            {{ getChordDisplayName(chord) }}
          </button>
          <button class="remove-button" @click="removeChord(chord.id)">
            ×
          </button>

          <div v-if="editingChordId === chord.id" class="editor-popover">
            <select v-model="chord.root">
              <option v-for="note in NOTES" :key="note" :value="note">
                {{ note }}
              </option>
            </select>
            <select v-model="chord.quality">
              <option v-for="q in QUALITIES" :key="q.value" :value="q.value">
                {{ q.text }}
              </option>
            </select>
            <button @click="editingChordId = null" class="close-editor">
              OK
            </button>
          </div>
        </div>
        <button class="add-button" @click="addChord()">+</button>
      </div>

      <div class="analyze-button-container">
        <button
          class="analyze-button"
          @click="analyzeProgression"
          :disabled="isLoading || isProgressionUnchanged"
        >
          {{ isLoading ? "Analyse..." : "Analyser la Progression" }}
        </button>
      </div>
    </div>

    <div v-if="isLoading" class="loading">Analyse en cours...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="analysisStore.hasResult" class="content-grid">
      <div class="left-column">
        <div class="results-box">
          <h2 class="result-title">
            --- {{ analysisResults.tonic }}
            {{ analysisResults.mode.replace(" (Original)", "") }} ---
          </h2>
          <div
            v-if="analysisResults.quality_analysis"
            class="detailed-analysis-container"
          >
            <div class="analysis-grid">
              <div
                v-for="(item, index) in analysisResults.quality_analysis"
                :key="index"
                class="analysis-card-container"
              >
                <div
                  class="card-inner"
                  :class="{ 'is-flipped': flippedCards.has(index) }"
                >
                  <div class="analysis-card card-front">
                    <div class="card-content">
                      <div class="chord-name">{{ item.chord }}</div>
                      <div
                        :class="{ foreign_chord: !item.is_diatonic }"
                        class="found-numeral"
                      >
                        {{ item.found_numeral }}
                      </div>
                      <div
                        v-if="
                          analysisResults.borrowed_chords &&
                          analysisResults.borrowed_chords[item.chord]
                        "
                        class="borrowed-info"
                      >
                        <em
                          >Emprunt de :
                          {{
                            analysisResults.borrowed_chords[item.chord].join(
                              ", "
                            )
                          }}</em
                        >
                      </div>
                    </div>
                    <button
                      v-if="shouldShowExpected(item)"
                      class="flip-button"
                      @click="toggleCardFlip(index)"
                    >
                      &#x21BA;
                    </button>
                  </div>

                  <div class="analysis-card card-back">
                    <div class="card-content">
                      <div class="expected-chord-name">
                        {{ item.expected_chord_name }}
                      </div>
                      <div class="expected-numeral">
                        {{ item.expected_numeral }}
                      </div>
                    </div>
                    <button class="flip-button" @click="toggleCardFlip(index)">
                      &#x21BA;
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="analysisResults.explanations" class="explanation-section">
            <button @click="toggleExplanation" class="explanation-toggle">
              {{ isExplanationVisible ? "Masquer" : "Afficher" }} l'explication
            </button>
            <div v-show="isExplanationVisible" class="explanation-content">
              <p>{{ analysisResults.explanations }}</p>
            </div>
          </div>

          <h3 v-if="analysisResults.substitutions">
            Table de Substitutions Modales :
          </h3>
          <table
            v-if="analysisResults.substitutions"
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
                v-for="(data, modeName) in analysisResults.substitutions"
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

/* Styles du constructeur de progression */
.builder-area {
  background-color: #2f2f2f;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}
.progression-builder {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
}
.chord-slot {
  position: relative;
}
.chord-button {
  padding: 1rem 1.5rem;
  font-size: 1.5rem;
  font-weight: 600;
  border-radius: 8px;
  border: 2px solid #555;
  background-color: #3c3c3c;
  color: white;
  cursor: pointer;
  min-width: 100px;
  transition: all 0.2s;
}
.chord-button:hover {
  border-color: #007bff;
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
.add-button {
  width: 50px;
  height: 50px;
  font-size: 2rem;
  border-radius: 50%;
  border: 2px dashed #555;
  background-color: transparent;
  color: #888;
  cursor: pointer;
  transition: all 0.2s;
}
.add-button:hover {
  background-color: #3c3c3c;
  color: white;
  border-color: #888;
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
  gap: 0.5rem;
  width: 220px;
}
.editor-popover select {
  width: 100%;
  padding: 0.5rem;
  font-size: 1rem;
  border-radius: 4px;
}
.editor-popover .close-editor {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background-color: #007bff;
  border: none;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}
.analyze-button-container {
  margin-top: 2rem;
  text-align: center;
}
.analyze-button {
  padding: 1rem 2rem;
  font-size: 1.2rem;
  border-radius: 8px;
  border: none;
  background-color: #007bff;
  color: white;
  cursor: pointer;
}
.analyze-button:disabled {
  background-color: #555;
  cursor: not-allowed;
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

.detailed-analysis-container {
  margin-bottom: 2rem;
}

.analysis-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1rem;
  background-color: #3a3a3a;
  border-radius: 8px;
}

.analysis-card {
  flex: 1;
  min-width: 120px;
  padding: 1rem 0 0 0;
  border-radius: 6px;
  background-color: #4a4a4a;
  text-align: center;
  border: 2px solid #555;
  transition: all 0.2s;
}

.analysis-card .chord-name {
  font-size: 1.8rem;
}

/* On met en évidence les cartes des accords non-diatoniques */

.analysis-card .found-numeral {
  font-family: "Courier New", Courier, monospace;
  font-size: 1.8rem;
  font-weight: bold;
  color: #a0cfff;
  margin: 0.5rem 0;
}

.analysis-card .foreign_chord {
  color: rgb(255, 95, 95) !important;
}

.analysis-card .expected-numeral {
  font-family: "Courier New", Courier, monospace;
  font-size: 1.8rem;
  font-weight: bold;
  color: #a0cfff;
  margin: 0.5rem 0;
}

.analysis-card .borrowed-info {
  font-size: 0.8rem;
}

.analysis-card .borrowed-info em {
  color: #fdcb6e;
}
.analysis-card-container {
  background-color: transparent;
  min-width: 140px;
  height: 180px;
  perspective: 1000px; /* Crée l'espace 3D */
  flex: 1;
}

.card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.6s; /* La durée de l'animation */
  transform-style: preserve-3d; /* Permet la 3D */
}

/* Applique la rotation quand la classe .is-flipped est présente */
.analysis-card-container .is-flipped {
  transform: rotateY(180deg);
}

/* Le .analysis-card est maintenant un panneau. On retire sa bordure */
.analysis-card {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden; /* Cache le dos du panneau quand il est retourné */
  border: 2px solid #555;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  box-sizing: border-box;
}

/* Positionnement et rotation du verso */
.card-back {
  background-color: #3d5a80; /* Une couleur différente pour le verso */
  border-color: #98c1d9;
  transform: rotateY(180deg);
}

.card-back-title {
  font-size: 0.9em;
  font-weight: bold;
  color: #e0fbfc;
}

.expected-chord-name {
  font-size: 1.8rem;
  font-weight: bold;
  color: green;
  margin: 0.5rem 0;
}

.flip-button {
  position: absolute;
  top: 5px;
  right: 5px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 16px;
  line-height: 24px;
}

.flip-button:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
