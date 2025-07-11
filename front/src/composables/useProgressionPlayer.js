import { ref } from "vue";
import * as Tone from "tone";

/**
 * Un Composable Vue.js pour gérer la lecture d'une progression musicale.
 *
 * @param {object} config - L'objet de configuration.
 * @param {Ref<Array>} config.progression - La Ref contenant la progression à jouer.
 * @param {object} config.tempoStore - Le store contenant les informations de tempo.
 * @param {Ref<boolean>} config.isLooping - La Ref pour savoir si la lecture doit boucler.
 * @param {Ref<boolean>} config.isMetronomeActive - La Ref pour activer/désactiver le métronome.
 * @param {object} config.metronome - L'instance du métronome de Tone.js.
 * @param {function} config.onPlayItemAsync - La fonction ASYNCHRONE à exécuter pour chaque item de la progression. Elle est responsable de jouer le son et d'attendre la durée nécessaire (await sleep).
 * @param {function} [config.onStart] - Callback optionnel exécuté au début de la lecture.
 * @param {function} [config.onStop] - Callback optionnel exécuté à la fin ou l'arrêt de la lecture.
 * @returns {{isPlaying: Ref<boolean>, currentlyPlayingIndex: Ref<number>, play: function, stop: function}}
 */
export function useProgressionPlayer({
  progression,
  tempoStore,
  isLooping,
  isMetronomeActive,
  metronome,
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
      onStop(); // Exécuter le nettoyage spécifique (ex: cancelAnimationFrame)
    }
    // Idéalement, votre instrument a une méthode pour tout couper
    // piano.releaseAll();
  };

  const play = async () => {
    if (isPlaying.value) return;
    if (Tone.getContext().state !== "running") {
      await Tone.start();
    }
    isPlaying.value = true;
    if (onStart) {
      onStart(); // Exécuter l'action de démarrage (ex: requestAnimationFrame)
    }

    try {
      do {
        for (const [index, item] of progression.value.entries()) {
          if (!isPlaying.value) break;

          // Condition générique pour sauter les items invalides
          if (
            !item ||
            (typeof item === "object" && !item.chord && !item.duration)
          ) {
            continue;
          }

          currentlyPlayingIndex.value = index;

          // Logique du métronome (commune aux deux)
          if (isMetronomeActive.value) {
            const beatDurationSec = tempoStore.beatDurationMs / 1000;
            for (let beat = 0; beat < item.duration; beat++) {
              if (isPlaying.value) {
                metronome.triggerAttack(
                  "C5",
                  Tone.now() + beat * beatDurationSec
                );
              }
            }
          }

          // Appel du callback spécifique qui gère la lecture de l'item ET l'attente
          await onPlayItemAsync({ item, index });
        }
        if (!isPlaying.value) break;
      } while (isLooping.value);
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
