import { createApp } from "vue";
import { createPinia } from "pinia";
import PrimeVue from "primevue/config";
import { definePreset } from "@primevue/themes";
import Aura from "@primevue/themes/aura";
import ToastService from "primevue/toastservice";
import ConfirmationService from "primevue/confirmationservice";
import Tooltip from "primevue/tooltip";

import App from "./App.vue";
import router from "./router";
import "primeicons/primeicons.css";
import "./styles.css";

// Re-map PrimeVue's primary to Baraquette gold so components inherit identity.
// Contrast text on gold is dark (#1A1A1A), never white (DESIGN.md §2.6).
const TradePreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: "#FBF7DE",
      100: "#F6EFB8",
      200: "#EFE389",
      300: "#E7D451",
      400: "#DEC52A",
      500: "#DBB600",
      600: "#B89800",
      700: "#8F7600",
      800: "#6B5800",
      900: "#4A3D00",
      950: "#2A2300",
    },
    colorScheme: {
      light: {
        primary: {
          color: "#DBB600",
          contrastColor: "#1A1A1A",
          hoverColor: "#B89800",
          activeColor: "#B89800",
        },
      },
    },
  },
});

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.use(PrimeVue, {
  theme: {
    preset: TradePreset,
    options: {
      darkModeSelector: ".never-dark",
      cssLayer: {
        name: "primevue",
        order: "tailwind-base, primevue, tailwind-utilities",
      },
    },
  },
});
app.use(ToastService);
app.use(ConfirmationService);
app.directive("tooltip", Tooltip);
app.mount("#app");
