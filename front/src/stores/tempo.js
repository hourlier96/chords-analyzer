// src/stores/tempo.js
import { defineStore } from "pinia";
import { ref, computed } from "vue";

export const useTempoStore = defineStore("tempo", () => {
  const bpm = ref(100);

  const beatDurationMs = computed(() => {
    return 60000 / bpm.value;
  });

  function setBpm(newBpm) {
    bpm.value = Math.max(40, Math.min(300, newBpm));
  }

  return {
    bpm,
    beatDurationMs,
    setBpm,
  };
});
