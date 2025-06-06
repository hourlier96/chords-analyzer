import { ref, computed, watch } from "vue";
import * as Tone from "tone";
import { useCorePlayer } from "@/composables/useCorePlayer.js";
import { useTempoStore } from "@/stores/tempo.js";

export const BEAT_WIDTH = 70;

/**
 * Composable pour gérer la lecture d'une progression d'accords.
 * @param {import('vue').Ref<Array>} progressionSource - La source réactive (ref ou computed) de la progression à jouer.
 * @param {Object} options - Options de configuration.
 * @param {Function} options.onPlayItemAsync - La fonction async pour jouer un seul item de la progression.
 */
export function useStatePlayer(progressionSource, { onPlayItemAsync }) {
  const tempoStore = useTempoStore();

  // Refs pour les contrôles du lecteur
  const timeSignature = ref("4/4");
  const isMetronomeActive = ref(true);
  const isLooping = ref(true);

  // Refs pour l'animation de la tête de lecture
  const playheadPosition = ref(0);
  const animationFrameId = ref(null);

  // Logique de calcul du layout de la grille (identique dans les deux composants)
  const beatsPerMeasure = computed(() => {
    return parseInt(timeSignature.value.split("/")[0], 10);
  });

  const totalBeats = computed(() => {
    const progressionDuration = progressionSource.value.reduce(
      (sum, chord) => sum + (chord.duration || 0),
      0
    );
    if (progressionDuration === 0) return beatsPerMeasure.value;

    const totalWithMargin =
      progressionDuration + (progressionSource.value.length > 0 ? 4 : 0);
    return (
      Math.ceil(totalWithMargin / beatsPerMeasure.value) * beatsPerMeasure.value
    );
  });

  // Logique d'animation
  const startAnimation = () => {
    playheadPosition.value = 0;
    const playbackStartTime = Tone.now() * 1000;

    const animatePlayhead = () => {
      if (!isPlaying.value) return;
      const elapsedTimeMs = Tone.now() * 1000 - playbackStartTime;
      const elapsedBeats = elapsedTimeMs / tempoStore.beatDurationMs;
      playheadPosition.value = elapsedBeats * BEAT_WIDTH;
      animationFrameId.value = requestAnimationFrame(animatePlayhead);
    };

    if (animationFrameId.value) cancelAnimationFrame(animationFrameId.value);
    animatePlayhead();
  };

  const stopAnimation = () => {
    if (animationFrameId.value) {
      cancelAnimationFrame(animationFrameId.value);
      animationFrameId.value = null;
    }
    playheadPosition.value = 0;
  };

  // Cœur du lecteur
  const { isPlaying, currentlyPlayingIndex, play, stop } = useCorePlayer({
    progression: progressionSource,
    tempoStore,
    isLooping,
    isMetronomeActive,
    beatsPerMeasure,
    onPlayItemAsync: onPlayItemAsync,
    onStart: startAnimation,
    onStop: (piano) => {
      stopAnimation();
      piano?.releaseAll();
    },
  });

  // Repositionne la tête de lecture au début lors d'une boucle
  watch(currentlyPlayingIndex, (newIndex, oldIndex) => {
    if (newIndex === 0 && oldIndex > newIndex) {
      startAnimation();
    }
  });

  return {
    // Constantes et état pour la vue
    BEAT_WIDTH,
    playheadPosition,
    beatsPerMeasure,
    totalBeats,

    // État et contrôles du lecteur
    isPlaying,
    currentlyPlayingIndex,
    timeSignature,
    isMetronomeActive,
    isLooping,

    // Fonctions à connecter aux événements
    playEntireProgression: play,
    stopSound: stop,
  };
}
