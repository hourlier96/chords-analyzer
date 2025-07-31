import { ref } from "vue";
import { defineStore } from "pinia";

export const useSettingsStore = defineStore(
  "settings",
  () => {
    const showNotes = ref(false);
    const audioMode = ref('chord');

    function toggleShowNotes() {
      showNotes.value = !showNotes.value;
    }

    function toggleAudioMode(mode) {
      audioMode.value = mode
    }

    return { showNotes, audioMode, toggleShowNotes, toggleAudioMode };
  },
  {
    persist: true,
  }
);
