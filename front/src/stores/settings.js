import { ref } from "vue";
import { defineStore } from "pinia";

export const useSettingsStore = defineStore(
  "settings",
  () => {
    const showNotes = ref(false);

    function toggleShowNotes() {
      showNotes.value = !showNotes.value;
    }

    return { showNotes, toggleShowNotes };
  },
  {
    persist: true,
  }
);
