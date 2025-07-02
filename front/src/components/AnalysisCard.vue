Vous avez tout à fait raison, mes excuses. J'ai détaillé les changements pour le
composant enfant mais j'ai omis de vous fournir le bloc de code final et
complet. Le voici. Ce code pour AnalysisCard.vue intègre la prop
isTritoneModeActive et utilise la propriété calculée showDiagonalSplit pour
afficher la vue en diagonale. Composant Enfant Final : AnalysisCard.vue Code
snippet

<template>
  <div class="analysis-card-container">
    <div class="card-inner" :class="{ 'is-flipped': isFlipped }">
      <div
        class="analysis-card card-front"
        :class="{ 'is-split': showDiagonalSplit }"
      >
        <div v-if="showDiagonalSplit" class="diagonal-container">
          <div class="tritone-chord-area">
            <div class="card-content">
              <div class="chord-name">{{ tritoneSubstitutionData.chord }}</div>
              <div class="found-numeral tritone_sub_chord">
                {{ tritoneSubstitutionData.found_numeral }}
              </div>
            </div>
          </div>
          <div class="original-chord-area">
            <div class="card-content">
              <div class="chord-name">{{ item.chord }}</div>
              <div
                class="found-numeral"
                :class="{ foreign_chord: !item.is_diatonic }"
              >
                {{ item.found_numeral }}
              </div>
            </div>
          </div>
        </div>

        <div v-else class="card-content">
          <div class="chord-name">{{ item.chord }}</div>
          <div
            class="found-numeral"
            :class="{ foreign_chord: !item.is_diatonic }"
          >
            {{ item.found_numeral }}
            <v-tooltip v-if="borrowedInfo" location="right">
              <template #activator="{ props }">
                <v-icon
                  v-bind="props"
                  :icon="mdiInformation"
                  size="x-small"
                ></v-icon>
              </template>
              <div class="borrowed-info-tooltip">
                <div v-for="(borrowed, idx) in borrowedInfo" :key="idx">
                  {{ analysis.result.tonic }}
                  {{ borrowed }}
                </div>
              </div>
            </v-tooltip>
          </div>
        </div>

        <v-tooltip
          v-if="shouldShowExpected"
          location="top"
          text="Swap vers l'accord diatonique"
        >
          <template #activator="{ props }">
            <button v-bind="props" class="flip-button" @click="toggleCardFlip">
              &#x21BA;
            </button>
          </template>
        </v-tooltip>
      </div>

      <div class="analysis-card card-back">
        <div class="card-content">
          <div class="expected-chord-name">{{ item.expected_chord_name }}</div>
          <div class="expected-numeral">{{ item.expected_numeral }}</div>
        </div>
        <v-tooltip location="top" text="Swap vers l'accord d'origine">
          <template #activator="{ props }">
            <button v-bind="props" class="flip-button" @click="toggleCardFlip">
              &#x21BA;
            </button>
          </template>
        </v-tooltip>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { mdiInformation } from "@mdi/js";

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
  analysis: {
    type: Object,
    required: true,
  },
  currentIndex: {
    type: Number,
    required: true,
  },
  // NOUVELLE PROP: Reçoit l'état depuis le composant parent
  isTritoneModeActive: {
    type: Boolean,
    required: true,
  },
});

const isFlipped = ref(false);

const toggleCardFlip = () => {
  isFlipped.value = !isFlipped.value;
};

const tritoneSubstitutionData = computed(() => {
  const substitutions = props.analysis.result.tritone_substitutions;
  if (!Array.isArray(substitutions)) return null;
  const foundSub = substitutions.find((sub) => sub[0] === props.item.chord);
  if (foundSub && foundSub[1]) {
    return {
      chord: foundSub[1],
      found_numeral: "subV",
      is_diatonic: false,
    };
  }
  return null;
});

const isTritoneSwapContextuallyValid = computed(() => {
  if (!tritoneSubstitutionData.value) {
    return false;
  }

  const progression = props.analysis.progression;
  const quality_analysis = props.analysis.result.quality_analysis;
  if (!quality_analysis || !progression || progression.length === 0) {
    return false;
  }

  const nextIndex = (props.currentIndex + 1) % progression.length;
  const nextChordData = progression[nextIndex];
  if (!nextChordData) return false;

  const nextChordAnalysis = quality_analysis.find(
    (entry) => entry.chord === `${nextChordData.root}${nextChordData.quality}`
  );
  if (!nextChordAnalysis?.found_numeral || !nextChordAnalysis.is_diatonic) {
    return false;
  }

  const allowedCadences = ["I", "i", "VI", "vi"];
  const baseNumeral = nextChordAnalysis.found_numeral
    .trim()
    .match(/^[ivIV]+/u)?.[0];
  if (!baseNumeral) return false;

  return allowedCadences.includes(baseNumeral);
});

/**
 * NOUVEAU : C'est la propriété clé qui contrôle l'affichage.
 * Elle est vraie uniquement si le mode global est activé ET
 * si l'accord actuel est contextuellement valide pour un swap.
 */
const showDiagonalSplit = computed(() => {
  return props.isTritoneModeActive && isTritoneSwapContextuallyValid.value;
});

const shouldShowExpected = computed(() => {
  return (
    !props.item.is_diatonic &&
    !!props.item.expected_chord_name &&
    props.item.expected_chord_name !== props.item.chord
  );
});

const borrowedInfo = computed(() => {
  return props.analysis.result.borrowed_chords?.[props.item.chord];
});
</script>

<style scoped>
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

.analysis-card .tritone_sub_chord {
  color: #fdcb6e !important;
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

.analysis-card.is-swapped {
  border-color: #fdcb6e;
  box-shadow: 0 0 8px #69f0ae;
}

.swaap-button.is-swapped {
  opacity: 1;
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

.analysis-card.is-split {
  border-color: #fdcb6e;
  background: linear-gradient(
    to top left,
    rgba(74, 74, 74, 0.5) 0%,
    rgba(74, 74, 74, 0.5) 49%,
    #fdcb6e 50%,
    rgba(60, 60, 60, 0.5) 51%,
    rgba(60, 60, 60, 0.5) 100%
  );
}

.analysis-card.is-split {
  border-color: #fdcb6e;
  background: linear-gradient(
    to top left,
    rgba(74, 74, 74, 0.5) 0%,
    rgba(74, 74, 74, 0.5) 49%,
    #fdcb6e 50%,
    rgba(60, 60, 60, 0.5) 51%,
    rgba(60, 60, 60, 0.5) 100%
  );
}

.analysis-card.is-split {
  border-color: #fdcb6e;
  background: linear-gradient(
    to top left,
    rgba(74, 74, 74, 0.5) 0%,
    rgba(74, 74, 74, 0.5) 49%,
    #fdcb6e 50%,
    rgba(60, 60, 60, 0.5) 51%,
    rgba(60, 60, 60, 0.5) 100%
  );
}

.diagonal-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.original-chord-area,
.tritone-chord-area {
  position: absolute;
  width: 100%;
  height: 100%;
}

/* --- Accord d'origine (G7) --- */
.original-chord-area {
  /* MODIFIÉ : Crée le triangle en bas à droite */
  clip-path: polygon(100% 0, 100% 100%, 0 100%);
  text-align: right;
}
.original-chord-area .card-content {
  position: absolute;
  /* MODIFIÉ : Positionne le texte en bas à droite */
  bottom: 1.5rem;
  right: 1.5rem;
}

/* --- Accord de substitution (subV) --- */
.tritone-chord-area {
  /* MODIFIÉ : Crée le triangle en haut à gauche */
  clip-path: polygon(0 0, 100% 0, 0 100%);
  text-align: left;
}
.tritone-chord-area .card-content {
  position: absolute;
  /* MODIFIÉ : Positionne le texte en haut à gauche */
  top: 1.5rem;
  left: 1.5rem;
}

.original-chord-area .card-content,
.tritone-chord-area .card-content {
  justify-content: initial;
  align-items: initial;
}

.original-chord-area .chord-name,
.tritone-chord-area .chord-name,
.original-chord-area .found-numeral,
.tritone-chord-area .found-numeral {
  font-size: 1.5rem;
  line-height: 1.2;
}
.flip-button,
.swap-button {
  position: absolute;
  top: 5px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 16px;
  line-height: 24px;
  transition:
    background-color 0.2s,
    opacity 0.2s;
  /* Centrage de l'icône */
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0;
}

.flip-button:hover,
.swap-button:hover,
.swap-button.is-active {
  background: rgba(255, 255, 255, 0.2);
  opacity: 1;
}

.flip-button {
  right: 5px;
}

.swap-button {
  left: 5px; /* Positionnement à gauche */
  opacity: 0.6;
}

.borrowed-info-tooltip {
  max-width: 250px;
  white-space: normal;
  text-align: left;
  padding: 8px;
  color: #fdcb6e; /* Jaune/Or, comme dans le style inline original */
}

.borrowed-info-tooltip div {
  margin-bottom: 4px;
}
</style>
