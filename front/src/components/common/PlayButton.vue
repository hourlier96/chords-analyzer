<template>
  <button class="listen-button" @click.stop="play">
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      width="20"
      height="20"
    >
      <path d="M8 5v14l11-7z" />
    </svg>
  </button>
</template>

<script setup>
import * as Tone from "tone";

const props = defineProps({
  // L'objet accord contenant la fondamentale (root) et la qualité (quality)
  chord: { type: Object, required: true },
  // L'instance du sampler Tone.js partagée
  piano: { type: Object, required: true },
});

/**
 * Joue les notes de l'accord en arpège.
 */
async function play() {
  // S'assure que le contexte audio est démarré
  if (Tone.getContext().state !== "running") {
    await Tone.start();
  }

  // Appelle la méthode directement depuis l'objet piano
  props.piano.play(props.chord);
}
</script>

<style scoped>
.listen-button {
  position: absolute;
  bottom: -10px;
  left: -10px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 5;
  transition: background-color 0.2s;
}

.listen-button:hover {
  background-color: #0056b3;
}
</style>
