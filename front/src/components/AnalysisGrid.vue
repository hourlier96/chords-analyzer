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
          v-if="
            showSecondaryDominants &&
            secondaryDominantsMap.has(item.chord) &&
            !tritoneSwapStates[index]
          "
          class="secondary-dominant-card"
        >
          <div class="card-content">
            <div class="chord-name">
              {{ secondaryDominantsMap.get(item.chord) }}
            </div>
            <div class="arrow-symbol">→</div>
          </div>
        </div>

        <AnalysisCard
          :key="index"
          :item="item"
          :analysisResults="analysisResults"
          @tritone-swap-toggled="
            (isSwapped) => handleTritoneToggle(index, isSwapped)
          "
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import AnalysisCard from "@/components/AnalysisCard.vue";

// Définition des props que le composant attend de son parent
const props = defineProps({
  analysisResults: {
    type: Object,
    required: true,
  },
});

const showSecondaryDominants = ref(false);
const tritoneSwapStates = ref({});

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

const handleTritoneToggle = (index, isSwapped) => {
  tritoneSwapStates.value[index] = isSwapped;
};
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
</style>
