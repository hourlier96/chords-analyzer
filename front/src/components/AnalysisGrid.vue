<template>
  <div
    v-if="analysisResults && analysisResults.quality_analysis"
    class="detailed-analysis-container"
  >
    <div class="analysis-header">
      <div class="header-controls">
        <button
          @click="showSecondaryDominants = !showSecondaryDominants"
          class="control-icon-button"
          :class="{ 'is-active': showSecondaryDominants }"
          :title="
            showSecondaryDominants
              ? 'Cacher les dominantes secondaires'
              : 'Afficher les dominantes secondaires'
          "
        >
          <span style="font-size: 15px; font-weight: bold">V/</span>
        </button>
      </div>
    </div>

    <div class="analysis-grid">
      <div
        v-for="(item, index) in analysisResults.quality_analysis"
        :key="`group-${index}`"
        class="chord-progression-group"
      >
        <div
          v-if="showSecondaryDominants && secondaryDominantsMap.has(item.chord)"
          class="secondary-dominant-card"
        >
          <div class="card-content">
            <div class="chord-name">
              {{ secondaryDominantsMap.get(item.chord) }}
            </div>
            <div class="arrow-symbol">→</div>
          </div>
        </div>

        <div class="analysis-card-container">
          <div
            class="card-inner"
            :class="{ 'is-flipped': flippedCards.has(index) }"
          >
            <div class="analysis-card card-front">
              <div class="card-content">
                <div class="chord-name">{{ item.chord }}</div>
                <div
                  class="found-numeral"
                  :class="{ foreign_chord: !item.is_diatonic }"
                >
                  {{ item.found_numeral }}
                </div>
                <v-tooltip
                  v-if="
                    analysisResults.borrowed_chords &&
                    analysisResults.borrowed_chords[item.chord]
                  "
                >
                  <template #activator="{ props }">
                    <v-icon v-bind="props" :icon="mdiInformation"></v-icon>
                  </template>
                  <div
                    class="borrowed-info-tooltip"
                    style="
                      max-width: 250px;
                      white-space: normal;
                      text-align: left;
                      padding: 8px;
                    "
                  >
                    <div
                      v-for="(borrowed, idx) in analysisResults.borrowed_chords[
                        item.chord
                      ]"
                      :key="idx"
                      style="margin-bottom: 4px; color: #fdcb6e"
                    >
                      {{ borrowed }}
                    </div>
                  </div>
                </v-tooltip>
              </div>

              <button
                v-if="shouldShowExpected(item)"
                class="flip-button"
                @click="toggleCardFlip(index)"
                title="Afficher l'accord attendu"
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
              <button
                class="flip-button"
                @click="toggleCardFlip(index)"
                title="Retourner à l'accord trouvé"
              >
                &#x21BA;
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { mdiInformation } from "@mdi/js";

const CORE_QUALITIES = {
  // Majeurs
  "": "major",
  M: "major",
  maj: "major",
  maj7: "major",
  "maj7#5": "major",
  maj9: "major",

  // Mineurs
  m: "minor",
  min: "minor",
  m7: "minor",
  "m(maj7)": "minor",
  m6: "minor",
  m9: "minor",
  m11: "minor",

  // Dominants
  7: "dominant",
  "7b5": "dominant",
  "7#5": "dominant",
  "7b9": "dominant",
  "7#9": "dominant",
  13: "dominant",

  // Diminués
  m7b5: "diminished", // demi-diminué (øm7b5)
  dim: "diminished", // triade diminuée
  dim7: "diminished", // diminué 7 (o7)
  d: "diminished", // raccourci informel

  // Augmentés
  aug: "augmented",
  "+": "augmented", // raccourci informel

  // Suspendus (pas tonales, mais utile pour filtres)
  sus2: "suspended",
  sus4: "suspended",
};

// Définition des props que le composant attend de son parent
const props = defineProps({
  analysisResults: {
    type: Object,
    required: true,
  },
});

const showSecondaryDominants = ref(false);

/**
 * Creates a Map where the key is the target chord and the value is its secondary dominant.
 * This makes it easy and efficient to look up in the template.
 */
const secondaryDominantsMap = computed(() => {
  const map = new Map();
  if (props.analysisResults && props.analysisResults.secondary_dominants) {
    // The prop is an object of tuples [secondary_dominant, target_chord]
    for (const dominantPair of Object.values(
      props.analysisResults.secondary_dominants
    )) {
      const [secondaryChord, targetChord] = dominantPair;
      map.set(targetChord, secondaryChord);
    }
  }
  return map;
});

const flippedCards = ref(new Set());

function shouldShowExpected(analysisItem) {
  const {
    found_quality,
    expected_quality,
    found_numeral,
    expected_numeral,
    is_diatonic,
  } = analysisItem;

  if (is_diatonic) return false;

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
</script>

<style scoped>
.detailed-analysis-container {
  margin-bottom: 2rem;
}

/* NOUVEAU : Styles pour le header et ses contrôles */
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
    border-color 0.2s;
}

.header-controls button:hover {
  background-color: #5a5a5a;
  border-color: #777;
}

.header-controls .control-icon-button {
  background-color: #4a4a4a;
  color: #edf2f4;
  border: 1px solid #555;
  border-radius: 50%; /* Makes the button round */
  width: 40px; /* Defines a fixed width */
  height: 40px; /* Defines a fixed height */
  padding: 0; /* Removes default padding */
  font-weight: bold;
  font-family: "Courier New", Courier, monospace;
  font-size: 1rem;
  cursor: pointer;
  transition:
    background-color 0.2s,
    border-color 0.2s;

  /* Flexbox for perfect centering of the text */
  display: flex;
  justify-content: center;
  align-items: center;
}

.header-controls .control-icon-button:hover {
  background-color: #5a5a5a;
  border-color: #777;
}

.control-icon-button.is-active {
  color: #000000;
  background-color: #6497cc;
}

.analysis-grid {
  display: grid;
  /* Default to a single, full-width column on narrow screens */
  grid-template-columns: 1fr;
  gap: 1.5rem;
  padding: 1rem;
  background-color: #3a3a3a;
  border-radius: 8px;
}

/* Apply the multi-column layout only when the screen is wide enough for at least two items */
@media (min-width: 600px) {
  .analysis-grid {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  }
}

.chord-progression-group {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  justify-content: center; /* Add this line to center the cards */
}

/* NEW: Styles for the secondary dominant card */
.secondary-dominant-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;
  min-width: 120px;
  height: 180px;
  padding: 1rem;
  border-radius: 6px;
  background-color: #4f3b78; /* Distinct purple color */
  border: 2px solid #7a5ba9;
  color: #e6dff2;
  text-align: center;
}

.secondary-dominant-card .chord-name {
  font-size: 1.8rem;
  font-weight: bold;
}

.secondary-dominant-card .arrow-symbol {
  font-size: 2rem;
  line-height: 1;
  margin: 0.25rem 0;
  color: #c3aedc;
}

.secondary-dominant-card .sd-label {
  font-family: "Courier New", Courier, monospace;
  font-size: 1.2rem;
  font-weight: bold;
  color: #c3aedc;
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

.analysis-card .card-content {
  /* This ensures content is centered within the flexbox layout */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  flex-grow: 1;
}

.analysis-card .chord-name {
  font-size: 1.8rem;
}

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

.analysis-card-container .is-flipped {
  transform: rotateY(180deg);
}

.analysis-card {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden; /* Cache le dos du panneau quand il est retourné */
  border: 2px solid #555;
  display: flex;
  flex-direction: column;
  justify-content: space-between; /* Pushes button to the bottom */
  align-items: center;
  padding: 1rem;
  box-sizing: border-box;
}

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
  color: green; /* Changed to a more visible color */
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
