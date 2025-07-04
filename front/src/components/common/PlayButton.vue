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
import { piano } from "@/sampler.js";

const props = defineProps({
  chord: { type: Object, required: true },
});

async function play() {
  if (Tone.getContext().state !== "running") {
    await Tone.start();
  }

  piano.play(props.chord);
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
  border: 1 px solid;
  background-color: #25303b;
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
