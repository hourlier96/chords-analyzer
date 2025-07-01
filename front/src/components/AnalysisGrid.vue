<template>
  <div
    v-if="analysisResults && analysisResults.quality_analysis"
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
                class="found-numeral"
                :class="{ foreign_chord: !item.is_diatonic }"
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
                    analysisResults.borrowed_chords[item.chord].join(", ")
                  }}</em
                >
              </div>
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
</template>

<script setup>
import { ref } from "vue";

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

// Définition des props que le composant attend de son parent
const props = defineProps({
  analysisResults: {
    type: Object,
    required: true,
  },
});

// État réactif pour suivre les cartes retournées (on utilise un Set pour l'efficacité)
const flippedCards = ref(new Set());

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
</script>

<style scoped>
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
