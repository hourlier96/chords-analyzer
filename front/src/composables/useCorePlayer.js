import { ref } from "vue";
import { piano } from "@/sampler.js";
import { metronome } from "@/metronome.js"; // AJOUT: On importe notre module métronome
import * as Tone from "tone";

/**
 * Un Composable Vue.js pour gérer la lecture d'une progression musicale.
 *
 * @param {object} config - L'objet de configuration.
 * @param {Ref<Array>} config.progression - La Ref contenant la progression à jouer.
 * @param {object} config.tempoStore - Le store contenant les informations de tempo.
 * @param {Ref<boolean>} config.isLooping - La Ref pour savoir si la lecture doit boucler.
 * @param {Ref<boolean>} config.isMetronomeActive - La Ref pour activer/désactiver le métronome.
 * @param {Ref<number>} config.beatsPerMeasure - La Ref indiquant le nombre de temps par mesure.
 * @param {function} config.onPlayItemAsync - La fonction ASYNCHRONE à exécuter pour chaque item de la progression.
 * @param {function} [config.onStart] - Callback optionnel exécuté au début de la lecture.
 * @param {function} [config.onStop] - Callback optionnel exécuté à la fin ou l'arrêt de la lecture.
 * @returns {{isPlaying: Ref<boolean>, currentlyPlayingIndex: Ref<number>, play: function, stop: function}}
 */
export function useCorePlayer({
  progression,
  tempoStore,
  isLooping,
  isMetronomeActive,
  beatsPerMeasure,
  onPlayItemAsync,
  onStart,
  onStop,
}) {
  const isPlaying = ref(false);
  const currentlyPlayingIndex = ref(-1);

  const stop = () => {
    if (!isPlaying.value) return;
    isPlaying.value = false;
    currentlyPlayingIndex.value = -1;
    if (onStop) {
      onStop();
    }
    piano.releaseAll();
  };

  const play = async () => {
    if (isPlaying.value) return;
    if (Tone.getContext().state !== "running") {
      await Tone.start();
    }
    isPlaying.value = true;
    if (onStart) {
      onStart();
    }

    let globalBeatCounter = 0;

    try {
      do {
        for (const [index, item] of progression.value.entries()) {
          if (!isPlaying.value) break;

          if (
            !item ||
            (typeof item === "object" && !item.chord && !item.duration)
          ) {
            continue;
          }

          currentlyPlayingIndex.value = index;

          if (isMetronomeActive.value) {
            const beatDurationSec = tempoStore.beatDurationMs / 1000;
            // On boucle sur la durée de l'accord actuel
            for (let localBeat = 0; localBeat < item.duration; localBeat++) {
              if (isPlaying.value) {
                const time = Tone.now() + localBeat * beatDurationSec;
                // On appelle notre module avec le compteur global
                metronome.click(globalBeatCounter, beatsPerMeasure.value, time);
                globalBeatCounter++; // On incrémente le compteur global
              }
            }
          }
          await onPlayItemAsync({ item, index });
        }

        // Si on boucle, on réinitialise le compteur global
        if (isLooping.value && isPlaying.value) {
          globalBeatCounter = 0;
        }
      } while (isLooping.value && isPlaying.value);
    } catch (error) {
      console.error("Erreur durant la lecture :", error);
    } finally {
      stop();
    }
  };

  return {
    isPlaying,
    currentlyPlayingIndex,
    play,
    stop,
  };
}
