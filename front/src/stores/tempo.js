// src/stores/tempo.js
import { defineStore } from "pinia";
import { ref, computed } from "vue";

export const useTempoStore = defineStore("tempo", () => {
  // --- STATE ---
  const bpm = ref(120); // Valeur par défaut du BPM

  // --- GETTERS ---
  /**
   * Calcule la durée d'un temps (beat) en millisecondes.
   * C'est la valeur qui sera utilisée pour les `sleep` ou les événements Tone.js.
   */
  const beatDurationMs = computed(() => {
    // 60,000 millisecondes dans une minute / BPM
    return 60000 / bpm.value;
  });

  // --- ACTIONS ---
  function setBpm(newBpm) {
    // On s'assure que le BPM reste dans une plage raisonnable
    bpm.value = Math.max(20, Math.min(300, newBpm));
  }

  return {
    bpm,
    beatDurationMs,
    setBpm,
  };
});
