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
      :piano="piano"
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
import * as Tone from "tone";
import { useAnalysisStore } from "@/stores/analysis.js";
import { mdiInformation, mdiWaveform, mdiMusicCircle, mdiCog } from "@mdi/js";
import { ALL_NOTES_FLAT, CHORD_FORMULAS } from "@/constants.js"; // Make sure path is correct
import AnalysisGrid from "@/components/analysis/AnalysisGrid.vue";
import ChordProgressionBuilder from "@/components/progression/ChordProgressionBuilder.vue";

const analysisStore = useAnalysisStore();

const isSettingsOpen = ref(false);

const defaultProgression = [
  { id: 1, root: "C", quality: "" },
  { id: 2, root: "D", quality: "m" },
  { id: 3, root: "G", quality: "7" },
  { id: 4, root: "A", quality: "m7" },
];

/**
 * Calculates the notes for a given chord, keeping them in a balanced, centered range.
 * @param {object} chord - The chord object with { root, quality }.
 * @returns {string[]} An array of notes (e.g., ["C4", "E4", "G4"]).
 */
function getNotesForChord(chord) {
  const intervals = CHORD_FORMULAS[chord.quality];
  if (!intervals) return [];

  const rootIndex = ALL_NOTES_FLAT.indexOf(chord.root);
  if (rootIndex === -1) return [];

  let octave = 4;
  if (
    chord.root.startsWith("G") ||
    chord.root.startsWith("A") ||
    chord.root.startsWith("B")
  ) {
    octave = 3;
  }
  // --------------------------------------------------

  return intervals.map((interval) => {
    const noteIndex = (rootIndex + interval) % 12;
    const currentOctave = octave + Math.floor((rootIndex + interval) / 12);
    return `${ALL_NOTES_FLAT[noteIndex]}${currentOctave}`;
  });
}

const compressor = new Tone.Compressor({
  threshold: -12, // Le seuil à partir duquel la compression s'active
  ratio: 4, // Le ratio de compression (4:1)
}).toDestination();

const eq = new Tone.EQ3({
  low: -2, // Baisser un peu les basses pour éviter un son boueux
  mid: 0,
  high: 2, // Augmenter les aigus pour plus de brillance
});
const reverb = new Tone.Reverb({
  decay: 2.5, // La queue de la réverbération
  wet: 0.3, // La quantité d'effet (0 à 1)
  preDelay: 0.01,
}).toDestination();

const playbackMode = ref("chords");

const piano = new Tone.Sampler({
  urls: {
    A1: "A1.mp3",
    C2: "C2.mp3",
    "D#2": "Ds2.mp3",
    "F#2": "Fs2.mp3",
    A2: "A2.mp3",
    C3: "C3.mp3",
    "D#3": "Ds3.mp3",
    "F#3": "Fs3.mp3",
    A3: "A3.mp3",
    C4: "C4.mp3",
    "D#4": "Ds4.mp3",
    "F#4": "Fs4.mp3",
    A4: "A4.mp3",
    C5: "C5.mp3",
    "D#5": "Ds5.mp3",
    "F#5": "Fs5.mp3",
    A5: "A5.mp3",
    C6: "C6.mp3",
    "D#6": "Ds6.mp3",
    "F#6": "Fs6.mp3",
    A6: "A6.mp3",
    C7: "C7.mp3",
  },
  release: 1.2,
  baseUrl: "https://tonejs.github.io/audio/salamander/",
}).chain(eq, compressor, reverb);

/**
 * Sets the playback mode for the piano.
 * @param {'arpeggio' | 'chord'} mode - The desired playback mode.
 */
function setPlaybackMode(mode) {
  if (mode === "arpeggio" || mode === "chord") {
    playbackMode.value = mode;
  }
}

/**
 * Plays a chord (all notes together).
 * @param {object} chord - The chord object with { root, quality }.
 */
piano.playChord = function (chord) {
  this.releaseAll();
  const notes = getNotesForChord(chord);
  if (notes.length > 0) {
    this.triggerAttack(notes);
  }
};

/**
 * Plays a chord as an arpeggio.
 * @param {object} chord - The chord object with { root, quality }.
 */
piano.playArpeggio = function (chord) {
  this.releaseAll();
  const notes = getNotesForChord(chord);
  if (notes.length > 0) {
    const now = Tone.now();
    const baseVelocity = 0.6;
    const velocityIncrement = 0.1;
    notes.forEach((note, index) => {
      const velocity = Math.min(1.0, baseVelocity + index * velocityIncrement);
      this.triggerAttackRelease(note, "0.5s", now + index * 0.12, velocity);
    });
  }
};

/**
 * Plays a chord based on the current playbackMode.
 * @param {object} chord - The chord object with { root, quality }.
 */
piano.play = function (chord) {
  if (playbackMode.value === "arpeggio") {
    piano.playArpeggio(chord);
  } else {
    piano.playChord(chord);
  }
};

// --- End of Audio Logic ---

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
