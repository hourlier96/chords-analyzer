import { ref, computed } from "vue";
import { defineStore } from "pinia";

export const useAnalysisStore = defineStore(
  "analysis",
  () => {
    const lastAnalysis = ref({
      result: null,
      progression: null,
      model: null,
    });

    const hasResult = computed(() => lastAnalysis.value.result !== null);

    function setLastAnalysis(newResult, progressionSnapshot) {
      lastAnalysis.value.result = newResult;
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

    function setModel(newModel) {
      lastAnalysis.value.model = newModel;
    }

    function clearResult() {
      lastAnalysis.value.result = null;
      lastAnalysis.value.progression = null;
    }

    return {
      lastAnalysis,
      hasResult,
      setLastAnalysis,
      clearResult,
      setModel,
    };
  },
  {
    persist: true,
  }
);
