<template>
  <v-navigation-drawer
    id="sidebar"
    v-model="drawer"
    :rail="rail"
    :rail-width="56"
    :width="230"
    permanent
    @click="expandRail(true)"
  >
    <v-btn
      variant="text"
      :icon="rail ? 'mdi-chevron-right' : 'mdi-chevron-left'"
      @click.stop="expandRail(!rail)"
    />
    <v-divider />
    <v-list density="compact" nav>
      <v-list-item
        to="/presets"
        prepend-icon="mdi-music-note"
        title="Analyseur simple"
        value="table"
      />
      <v-list-item
        to="/advanced"
        prepend-icon="mdi-music"
        title="Analyseur complexe"
        value="form"
      />
    </v-list>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { ref } from 'vue'

let drawer = ref(true)
let rail = ref(true)

const emit = defineEmits(['expand'])

function expandRail(expand) {
  rail.value = expand
  emit('expand', expand)
}
</script>
