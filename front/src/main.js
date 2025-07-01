import "./assets/main.css";

import { createApp } from "vue";
import { createPinia } from "pinia";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";

import "vuetify/styles"; // Importe les styles de base de Vuetify
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
// L'importation la plus importante pour vos icônes !
import { mdi } from "vuetify/iconsets/mdi-svg";

import App from "./App.vue";
import router from "./router";

const app = createApp(App);

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

const vuetify = createVuetify({
  components,
  directives,
  // Configuration pour utiliser les icônes SVG de MDI
  icons: {
    defaultSet: "mdi", // Définit mdi comme jeu d'icônes par défaut
    sets: {
      mdi, // Enregistre le jeu d'icônes
    },
  },
});

app.use(pinia);
app.use(vuetify);
app.use(router);

app.mount("#app");
