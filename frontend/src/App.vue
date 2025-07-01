<template>
  <v-app :theme="appStore.theme">
    <v-navigation-drawer v-model="appStore.drawer" permanent>
      <v-list-item
        prepend-avatar="https://cdn-icons-png.flaticon.com/512/2165/2165544.png"
        title="arXiv RSS Filter Bot"
        nav
      >
        <template v-slot:append>
          <v-btn
            variant="text"
            icon="mdi-theme-light-dark"
            @click="appStore.toggleTheme"
          ></v-btn>
        </template>
      </v-list-item>

      <v-divider></v-divider>

      <v-list density="compact" nav>
        <v-list-item prepend-icon="mdi-view-dashboard" title="Dashboard" to="/" value="dashboard"></v-list-item>
        <v-list-item prepend-icon="mdi-cog" title="Configuration" to="/config" value="config"></v-list-item>
        <v-list-item prepend-icon="mdi-rss" title="Feeds" to="/feeds" value="feeds"></v-list-item>
        <v-list-item prepend-icon="mdi-information" title="About" to="/about" value="about"></v-list-item>
      </v-list>

      <template v-slot:append>
        <div class="pa-2">
          <v-btn
            block
            color="primary"
            prepend-icon="mdi-play"
            :loading="appStore.isRunning"
            :disabled="appStore.isRunning"
            @click="runBot"
          >
            Run Now
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <v-app-bar>
      <v-app-bar-nav-icon @click="appStore.toggleDrawer"></v-app-bar-nav-icon>
      <v-app-bar-title>{{ getTitle }}</v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn icon @click="openGithub">
        <v-icon>mdi-github</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <router-view></router-view>
    </v-main>

    <v-footer app>
      <span>&copy; {{ new Date().getFullYear() }} - arXiv RSS Filter Bot</span>
      <v-spacer></v-spacer>
      <span v-if="appStore.status.lastRun">Last Updated: {{ formatDateTime(appStore.status.lastRun) }}</span>
    </v-footer>
  </v-app>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useAppStore } from './stores/app'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const toast = useToast()
    const appStore = useAppStore()
    
    // Get current page title
    const getTitle = computed(() => {
      const path = router.currentRoute.value.path
      if (path === '/') return 'Dashboard'
      if (path === '/config') return 'Configuration'
      if (path === '/feeds') return 'RSS Feeds'
      if (path === '/about') return 'About'
      return 'arXiv RSS Filter Bot'
    })
    
    // Run the bot
    const runBot = async () => {
      try {
        const result = await appStore.runBot()
        if (result.success) {
          toast.success('RSS feed generated successfully!')
          router.push('/feeds')
        } else {
          toast.error(`Error: ${result.error}`)
        }
      } catch (error) {
        toast.error(`Error: ${error.message}`)
      }
    }
    
    // Open GitHub repo
    const openGithub = () => {
      window.open('https://github.com/Minfeng-Qi/arxiv-rss-filter-bot', '_blank')
    }
    
    // Fetch status on mount
    onMounted(() => {
      appStore.fetchStatus()
    })
    
    // 格式化日期和时间
    const formatDateTime = (dateString) => {
      if (!dateString) return 'Never'
      
      const date = new Date(dateString)
      return date.toLocaleString('default', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }
    
    return {
      appStore,
      getTitle,
      runBot,
      openGithub,
      formatDateTime
    }
  }
}
</script>

<style>
.v-navigation-drawer__append {
  position: absolute;
  bottom: 0;
  width: 100%;
  background-color: rgba(var(--v-theme-surface-variant));
  padding: 8px;
}
</style>