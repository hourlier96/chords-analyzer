<template>
  <div class="analysis-card-container">
    <div
      v-if="
        showSecondaryDominant && secondaryDominantChord && !showSubstitution
      "
      class="docked-secondary-dominant"
    >
      <div class="chord-name">{{ secondaryDominantChord }}</div>
    </div>
    <div class="card-inner" :class="{ 'is-flipped': isFlipped }">
      <div
        class="analysis-card card-front"
        :class="{ 'is-swapped': showSubstitution }"
      >
        <div v-if="showSubstitution" class="card-content">
          <div class="chord-name">{{ tritoneSubstitutionData.chord }}</div>
          <div class="found-numeral tritone_sub_chord">
            {{ tritoneSubstitutionData.found_numeral }}
          </div>
        </div>

        <div v-else class="card-content">
          <div class="chord-name">{{ item.chord }}</div>
          <div
            class="found-numeral"
            :class="{ foreign_chord: !item.is_diatonic }"
          >
            {{ item.found_numeral ? item.found_numeral : "" }}
            <v-tooltip v-if="borrowedInfo" location="right">
              <template #activator="{ props: tooltipProps }">
                <v-icon
                  v-bind="tooltipProps"
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
          <template #activator="{ props: tooltipProps }">
            <button
              v-bind="tooltipProps"
              class="flip-button"
              @click="toggleCardFlip"
            >
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
          <template #activator="{ props: tooltipProps }">
            <button
              v-bind="tooltipProps"
              class="flip-button"
              @click="toggleCardFlip"
            >
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
  isTritoneModeActive: {
    type: Boolean,
    required: true,
  },
  showSecondaryDominant: {
    type: Boolean,
    required: true,
  },
  secondaryDominantChord: {
    type: String,
    default: null,
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
  const currentChordName = props.item.chord;
  const nextIndex = (props.currentIndex + 1) % progression.length;
  const nextChordInProgression = progression[nextIndex];
  if (!nextChordInProgression) return false;

  const nextChordName = `${nextChordInProgression.root}${nextChordInProgression.quality}`;

  // Vérifier si l'accord est une dominante primaire ou secondaire résolvant sur sa cible.
  // On utilise la liste des dominantes identifiées par l'analyse pour une précision maximale.
  const allDominants = props.analysis.result.secondary_dominants;
  if (!allDominants) {
    return false; // Si la liste n'existe pas, on ne peut rien valider.
  }

  // On cherche une correspondance où l'accord actuel est la dominante (primaire ou secondaire)
  // et l'accord suivant est sa cible de résolution.
  const isAPertinentDominant = allDominants.some(
    ([dominantChord, targetChord, description]) => {
      // La description doit commencer par V7 pour être une fonction dominante.
      // Cela inclut "V7 (Dominante Primaire)" et "V7/..."
      return (
        dominantChord === currentChordName &&
        targetChord === nextChordName &&
        description.startsWith("V7")
      );
    }
  );

  return isAPertinentDominant;
});

const showSubstitution = computed(() => {
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
.analysis-card-container {
  position: relative;
  background-color: transparent;
  min-width: 140px;
  height: 180px;
  perspective: 1000px;
  flex: 1;
}

.docked-secondary-dominant {
  position: absolute;
  z-index: 10;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;
  min-width: 70px;
  height: 50px;
  padding: 0.5rem;
  border-radius: 6px;
  background-color: #4f3b78;
  border: 2px solid #7a5ba9;
  color: #e6dff2;
  text-align: center;
  box-shadow: 3px 3px 5px rgba(0, 0, 0, 0.3);
}

.docked-secondary-dominant .chord-name {
  font-size: 1.3rem;
  font-weight: bold;
}

.card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.analysis-card-container .is-flipped {
  transform: rotateY(180deg);
}

.analysis-card {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border: 2px solid #555;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  box-sizing: border-box;
  background-color: #4a4a4a;
  border-radius: 6px;
  transition: all 0.2s;
}

.analysis-card .card-content {
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

.analysis-card.is-swapped {
  border-color: #fdcb6e;
  box-shadow: 0 0 10px rgba(253, 203, 110, 0.5);
}

.card-back {
  background-color: #3d5a80;
  border-color: #98c1d9;
  transform: rotateY(180deg);
}

.expected-chord-name {
  font-size: 1.8rem;
  font-weight: bold;
  color: #a0cfff;
  margin: 0.5rem 0;
}

.expected-numeral {
  font-family: "Courier New", Courier, monospace;
  font-size: 1.8rem;
  font-weight: bold;
  color: #a0cfff;
  margin: 0.5rem 0;
}

.flip-button {
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
  transition: background-color 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0;
}

.flip-button:hover,
.mode-swap-button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.flip-button {
  right: 5px;
}

/* NOUVEAU : Style pour le bouton de swap de mode */
.mode-swap-button {
  left: 5px;
}

.borrowed-info-tooltip {
  max-width: 250px;
  white-space: normal;
  text-align: left;
  padding: 8px;
  color: #fdcb6e;
}

.borrowed-info-tooltip div {
  margin-bottom: 4px;
}
</style>
