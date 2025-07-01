import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { mdi } from 'vuetify/iconsets/mdi'
import { aliases, fa } from 'vuetify/iconsets/fa'
import '@mdi/font/css/materialdesignicons.css'

import App from './App.vue'
import Dashboard from './views/Dashboard.vue'
import Config from './views/Config.vue'
import Feeds from './views/Feeds.vue'
import About from './views/About.vue'

// Setup Vuetify
const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      fa,
      mdi
    }
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1867C0',
          secondary: '#5CBBF6',
          accent: '#e83e8c',
          success: '#4CAF50',
          info: '#2196F3',
          warning: '#FB8C00',
          error: '#FF5252'
        }
      },
      dark: {
        colors: {
          primary: '#2196F3',
          secondary: '#424242',
          accent: '#FF4081',
          success: '#4CAF50',
          info: '#2196F3',
          warning: '#FB8C00',
          error: '#FF5252'
        }
      }
    }
  }
})

// Setup router
const routes = [
  { path: '/', component: Dashboard },
  { path: '/config', component: Config },
  { path: '/feeds', component: Feeds },
  { path: '/about', component: About },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Create app
const app = createApp(App)

// Use plugins
app.use(createPinia())
app.use(router)
app.use(vuetify)
app.use(Toast, {
  transition: "Vue-Toastification__bounce",
  maxToasts: 3,
  newestOnTop: true
})

// Mount app
app.mount('#app')