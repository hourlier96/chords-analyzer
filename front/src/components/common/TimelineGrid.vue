<template>
  <div
    class="timeline-container"
    :style="{
      '--total-beats': totalBeats,
      '--beat-width': `${beatWidth}px`,
    }"
  >
    <div
      v-if="isPlaying"
      class="playhead"
      :style="{ transform: `translateX(${playheadPosition}px)` }"
    ></div>

    <div class="rhythm-timeline">
      <template v-for="beat in totalBeats" :key="`timeline-beat-${beat}`">
        <div
          class="beat-marker"
          :class="{ 'measure-start': (beat - 1) % beatsPerMeasure === 0 }"
          :style="{ 'grid-column-start': beat }"
        >
          <span
            v-if="(beat - 1) % beatsPerMeasure === 0"
            class="measure-number"
          >
            {{ Math.floor((beat - 1) / beatsPerMeasure) + 1 }}
          </span>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from "vue";

// Définition des propriétés que le composant attend de son parent
defineProps({
  // Le nombre total de temps à afficher dans la grille
  totalBeats: {
    type: Number,
    required: true,
  },
  // Le nombre de temps par mesure (ex: 4 pour une mesure en 4/4)
  beatsPerMeasure: {
    type: Number,
    required: true,
  },
  // La largeur en pixels de chaque temps, pour le calcul de la grille
  beatWidth: {
    type: Number,
    required: true,
  },
  // Indique si la lecture est en cours pour afficher/cacher la tête de lecture
  isPlaying: {
    type: Boolean,
    default: false,
  },
  // La position en pixels de la tête de lecture
  playheadPosition: {
    type: Number,
    default: 0,
  },
});
</script>

<style scoped>
/* Le conteneur principal est relatif pour positionner la tête de lecture */
.timeline-container {
  position: relative;
  width: 100%;
  padding-top: 20px; /* Espace pour les numéros de mesure */
}

.playhead {
  position: absolute;
  top: 15px; /* Ajusté pour être bien aligné avec les marqueurs */
  left: 0;
  width: 2px;
  height: calc(100% - 15px);
  background-color: #f44336; /* Rouge vif pour une bonne visibilité */
  z-index: 10;
  pointer-events: none; /* Pour ne pas interférer avec les clics */
  /* La transition est retirée ici pour laisser le parent la gérer via requestAnimationFrame pour plus de précision */
}

/* Grille CSS pour la timeline */
.rhythm-timeline {
  display: grid;
  grid-template-columns: repeat(var(--total-beats, 8), var(--beat-width));
  height: 20px; /* Hauteur de la ligne de temps */
  border-bottom: 1px solid #444;
}

.beat-marker {
  height: 100%;
  width: 1px;
  background-color: rgba(255, 255, 255, 0.2);
  justify-self: start;
  position: relative; /* Pour positionner le numéro de mesure */
}

/* Style pour le premier temps de chaque mesure */
.beat-marker.measure-start {
  width: 2px;
  background-color: rgba(255, 255, 255, 0.6);
}

.measure-number {
  position: absolute;
  top: -20px; /* Positionné au-dessus de la ligne */
  left: 4px;
  font-size: 12px;
  color: #aaa;
}
</style>
