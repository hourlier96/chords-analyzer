// Fichier: src/stores/analysis.js

import { ref, computed } from "vue";
import { defineStore } from "pinia";

export const useAnalysisStore = defineStore(
  "analysis",
  () => {
    // --- STATE ---
    // On stocke maintenant un objet qui contient tout ce qui est lié à la dernière analyse
    const lastAnalysis = ref({
      result: null, // Les données de l'API
      progression: null, // L'instantané de la progression
    });

    // --- GETTERS (Propriétés calculées du store) ---
    // Un getter pratique pour savoir s'il y a un résultat à afficher
    const hasResult = computed(() => lastAnalysis.value.result !== null);

    // --- ACTIONS ---
    // L'action met maintenant à jour à la fois le résultat ET l'instantané de la progression
    function setLastAnalysis(newResult, progressionSnapshot) {
      lastAnalysis.value.result = newResult;
      // Update de l'analyse pour y ajouter les inversions
      const enrichedResult = newResult.quality_analysis.map(
        (analysisItem, index) => {
          return {
            ...analysisItem,
            inversion: progressionSnapshot[index].inversion || 0,
          };
        }
      );
      lastAnalysis.value.progression = progressionSnapshot;
      lastAnalysis.value.result.quality_analysis = enrichedResult;
    }

    function clearResult() {
      lastAnalysis.value.result = null;
      lastAnalysis.value.progression = null;
    }

    // On retourne tout ce dont les composants auront besoin
    return {
      lastAnalysis,
      hasResult,
      setLastAnalysis,
      clearResult,
    };
  },
  {
    // Le plugin de persistance s'occupe de sauvegarder l'objet 'lastAnalysis' entier.
    persist: true,
  }
);
