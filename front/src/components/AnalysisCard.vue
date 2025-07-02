<template>
  <div class="analysis-card-container">
    <div class="card-inner" :class="{ 'is-flipped': isFlipped }">
      <div
        class="analysis-card card-front"
        :class="{ 'is-swapped': isShowingTritone && tritoneSubstitutionData }"
      >
        <v-tooltip location="top" text="Substitution tritonique">
          <template #activator="{ props }">
            <button
              v-if="tritoneSubstitutionData"
              v-bind="props"
              class="swap-button"
              :class="{ 'is-active': isShowingTritone }"
              @click="toggleTritoneSwap"
            >
              <v-icon :icon="mdiYinYang"></v-icon>
            </button>
          </template>
        </v-tooltip>

        <div class="card-content">
          <div class="chord-name">{{ displayItem.chord }}</div>
          <div
            class="found-numeral"
            :class="{
              tritone_sub_chord: isShowingTritone,
              foreign_chord: !displayItem.is_diatonic && !isShowingTritone,
            }"
          >
            {{ displayItem.found_numeral }}
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
                  {{ analysisResults.tonic }}
                  {{ borrowed }}
                </div>
              </div>
            </v-tooltip>
          </div>
        </div>

        <v-tooltip
          v-if="shouldShowExpected"
          location="top"
          :text="`Swap vers l'accord diatonique en ${analysisResults.tonic} ${analysisResults.mode}`"
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
import { mdiInformation, mdiYinYang } from "@mdi/js";

const emit = defineEmits(["tritone-swap-toggled"]);

const props = defineProps({
  item: {
    type: Object,
    required: true,
    default: () => ({
      chord: "N/A",
      found_numeral: "?",
      is_diatonic: true,
      expected_chord_name: "",
      expected_numeral: "",
    }),
  },
  analysisResults: {
    type: Object,
    required: true,
    default: () => ({ borrowed_chords: {}, tritone_substitution: {} }),
  },
});

const isFlipped = ref(false);
// NEW: État pour gérer l'affichage de la substitution tritonique
const isShowingTritone = ref(false);

const toggleCardFlip = () => {
  isFlipped.value = !isFlipped.value;
};

const toggleTritoneSwap = () => {
  isShowingTritone.value = !isShowingTritone.value;
  emit("tritone-swap-toggled", isShowingTritone.value);
};
// NEW: Propriété calculée qui récupère les données de la substitution si elle existe
const tritoneSubstitutionData = computed(() => {
  // 1. Récupère le tableau des substitutions depuis les props.
  const substitutions = props.analysisResults.tritone_substitutions;

  // 2. Sécurité : s'assure que les données sont bien un tableau avant de continuer.
  if (!Array.isArray(substitutions)) {
    return null;
  }

  // 3. Utilise .find() pour chercher le tableau interne dont le premier élément (sub[0])
  //    correspond à l'accord de la carte actuelle (props.item.chord).
  const foundSub = substitutions.find((sub) => sub[0] === props.item.chord);

  // 4. Vérifie si une substitution a été trouvée ET si le nom de l'accord substitué (foundSub[1]) n'est pas vide.
  if (foundSub && foundSub[1]) {
    // 5. Construit et retourne un nouvel objet "accord" complet pour la substitution.
    //    Ceci permet au reste du composant (comme 'displayItem') de fonctionner sans modification.
    return {
      chord: foundSub[1], // Le nom de l'accord de substitution, ex: 'F7'
      found_numeral: "subV", // Chiffrage romain standard pour une substitution tritonique
      is_diatonic: false, // Une substitution tritonique est par nature non diatonique
    };
  }

  // 6. Si aucune substitution valide n'est trouvée, retourne null.
  return null;
});

const displayItem = computed(() => {
  if (isShowingTritone.value && tritoneSubstitutionData.value) {
    return tritoneSubstitutionData.value;
  }
  return props.item;
});

const shouldShowExpected = computed(() => {
  return (
    !isShowingTritone.value &&
    !!props.item.expected_chord_name &&
    props.item.expected_chord_name !== props.item.chord &&
    !props.item.is_diatonic
  );
});

const borrowedInfo = computed(() => {
  return props.analysisResults.borrowed_chords?.[displayItem.value.chord];
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
