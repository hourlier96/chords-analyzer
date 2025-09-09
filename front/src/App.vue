<template>
  <v-app id="app">
    <NavigationDrawer @expand="adaptMargin($event)" />
    <NavBar />
    <v-main id="main-container" class="d-flex">
      <RouterView />
    </v-main>
  </v-app>
  <SnackBar />
</template>

<script setup lang="ts">
import NavigationDrawer from '@/components/NavigationDrawer.vue'
import NavBar from '@/components/NavBar.vue'
import SnackBar from '@/components/common/SnackBar.vue'
import { onMounted } from 'vue'

function adaptMargin(event) {
  const mainContainer = document.getElementById('main-container')
  mainContainer.style.marginLeft = event ? '56px' : '230px'
}

onMounted(() => {
  adaptMargin(true)
})
</script>

<style scoped>
#main-container {
  max-width: 95%;
  padding: calc(var(--navigation-bar-height) + 10px) 20px var(--navigation-bar-height) 20px;
}
</style>
