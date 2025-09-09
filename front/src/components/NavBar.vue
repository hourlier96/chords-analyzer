<template>
  <v-app-bar id="navbar" app :height="'--navigation-bar-height'" dark>
    <v-spacer />
    <v-menu v-model="showLang" :close-on-content-click="true" location="bottom">
      <template #activator="{ props: menuActivator }">
        <v-btn v-bind="menuActivator" aria-label="Changer la langue">
          <v-icon>
            <country-flag :country="getFlag(prefStore.lang)" size="normal" />
          </v-icon>
        </v-btn>
      </template>

      <v-list style="max-height: 200px; overflow-y: auto">
        <v-list-item
          v-for="(item, i) in countries_infos"
          :key="i"
          :value="item"
          @click="setLang(item.value)"
        >
          <template #prepend>
            <country-flag :country="item.flag" size="normal" class="flag-item" />
          </template>
          <v-list-item-title>{{ item.title }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>

    <v-dialog v-model="isSettingsOpen" max-width="500" close-on-back dark>
      <template #activator="{ props: activatorProps }">
        <v-btn v-bind="activatorProps" aria-label="Ouvrir les paramètres">
          <v-icon icon="mdi-cog" size="x-large" />
        </v-btn>
      </template>

      <v-card class="settings-container" width="300px">
        <v-card-title class="text-h5"> Paramètres </v-card-title>
        <v-card-text>
          <div class="setting-item-modal">
            Thème
            <v-tooltip
              location="top"
              :text="prefStore.isDark ? 'Passer en thème clair' : 'Passer en thème sombre'"
            >
              <template #activator="{ props: tooltipProps }">
                <button
                  v-bind="tooltipProps"
                  @click="prefStore.toggleTheme(theme)"
                  class="control-icon-button"
                >
                  <v-icon
                    :icon="prefStore.isDark ? 'mdi-weather-sunny' : 'mdi-moon-waning-crescent'"
                  />
                </button>
              </template>
            </v-tooltip>
          </div>

          <div class="setting-item-modal">
            Affichage des notes
            <v-tooltip
              location="top"
              :text="
                settingsStore.showNotes
                  ? 'Cacher les notes des accords'
                  : 'Afficher les notes des accords'
              "
            >
              <template #activator="{ props: tooltipProps }">
                <button
                  v-bind="tooltipProps"
                  @click="settingsStore.toggleShowNotes()"
                  class="control-icon-button"
                >
                  <v-icon
                    :icon="settingsStore.showNotes ? 'mdi-music-note' : 'mdi-music-note-off'"
                  />
                </button>
              </template>
            </v-tooltip>
          </div>
          <div class="setting-item-modal">
            Mode de lecture audio
            <v-tooltip
              location="top"
              :text="
                settingsStore.audioMode === 'arpeggio'
                  ? 'Passer en mode accords plaqués'
                  : 'Passer en mode arpège'
              "
            >
              <template #activator="{ props: tooltipProps }">
                <button
                  v-bind="tooltipProps"
                  @click="
                    settingsStore.toggleAudioMode(
                      settingsStore.audioMode === 'arpeggio' ? 'chord' : 'arpeggio'
                    )
                  "
                  class="control-icon-button"
                >
                  <v-icon
                    :icon="
                      settingsStore.audioMode === 'arpeggio' ? 'mdi-waveform' : 'mdi-music-circle'
                    "
                  />
                </button>
              </template>
            </v-tooltip>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue-darken-1" text="Fermer" @click="isSettingsOpen = false"></v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-app-bar>
</template>

<script setup lang="ts">
import imgSrc from '@/assets/logo.svg'
import { ref } from 'vue'
import { useLocale, useTheme } from 'vuetify'
import { usePreferencesStore } from '@/stores/preferences.ts'
import { useSettingsStore } from '@/stores/settings.ts'
import { onMounted } from 'vue'
import CountryFlag from 'vue-country-flag-next'
import { countries_infos } from '@/../i18n/index.js'

const theme = useTheme()
const { current } = useLocale()
const prefStore = usePreferencesStore()
const settingsStore = useSettingsStore()

const showLang = ref(false)
const isSettingsOpen = ref(false)

onMounted(() => {
  theme.change(prefStore.isDark ? 'customDarkTheme' : 'customLightTheme')
  setLang(prefStore.lang)
})

function openDocumentation() {
  window.open('https://vuejs.org/guide/quick-start.html', '_blank')
}

function getFlag(lang) {
  return countries_infos.find((item) => item.value === lang).flag
}
function setLang(lang) {
  // Vuetify translation
  current.value = lang
  // Custom translation
  prefStore.setLang(lang)
  showLang.value = false
}
</script>

<style scoped>
#navbar {
  height: var(--navigation-bar-height);
  overflow: visible;
}

.v-toolbar,
.v-toolbar__content {
  overflow: visible !important;
}

.flag-list {
  position: absolute;
  top: 50px;
  right: 0px;
  padding: 0;
  background-color: var(--v-primary-base);
  border-radius: 0px 0px 0px 10px;
}

.normal-flag {
  margin: 0em -0.9em 0px -1em !important;
}

.flag-item {
  margin: 0px 0px 0px 0px !important;
}
</style>
