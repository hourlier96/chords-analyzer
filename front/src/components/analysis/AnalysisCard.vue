<template>
  <div class="analysis-card-container">
    <PlayButton :chord="extractChordComponents(item)" :piano="piano" />
    <div
      v-if="showSecondaryDominant && secondaryDominantChord != 'N/A'"
      class="docked-secondary-dominant"
    >
      <div class="chord-name">{{ secondaryDominantChord }}</div>
    </div>
    <div class="card-inner" :class="{ 'is-flipped': isFlipped }">
      <div class="analysis-card card-front">
        <div class="card-content">
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

import { piano } from "@/sampler.js";
import PlayButton from "@/components/common/PlayButton.vue";

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

function extractChordComponents(data) {
  const chord = data.chord || "";

  // Regex pour extraire la tonique (A-G avec # ou b) + qualité
  const match = chord.match(/^([A-G][b#]?)(.*)$/);
  if (!match) {
    return { root: null, quality: null };
  }

  const [, root, quality] = match;
  return { root, quality };
}
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
  height: 30px;
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
