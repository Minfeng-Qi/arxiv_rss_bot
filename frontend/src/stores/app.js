// Pinia Store for app-wide state
import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useAppStore = defineStore('app', () => {
  // State
  const theme = ref(localStorage.getItem('theme') || 'light')
  const drawer = ref(true)
  const isRunning = ref(false)
  const status = ref({
    lastRun: null,
    lastFeed: null,
    paperCount: 0,
    papers: []
  })

  // Actions
  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    localStorage.setItem('theme', theme.value)
  }

  function toggleDrawer() {
    drawer.value = !drawer.value
  }

  async function runBot() {
    try {
      isRunning.value = true
      const response = await axios.post('/api/run')
      
      if (response.data.success) {
        await fetchStatus()
        return { success: true }
      } else {
        return { success: false, error: response.data.error }
      }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || error.message 
      }
    } finally {
      isRunning.value = false
    }
  }

  async function fetchStatus() {
    try {
      // 直接从status API获取所有需要的数据
      const statusResponse = await axios.get('/api/status')
      if (statusResponse.data.success && statusResponse.data.status) {
        // 更新状态信息
        status.value.lastRun = statusResponse.data.status.lastRun
        status.value.paperCount = statusResponse.data.status.paperCount
        status.value.lastFeed = statusResponse.data.status.latestOutput
        status.value.papers = statusResponse.data.status.papers || []
      }
    } catch (error) {
      console.error('Error fetching status:', error)
    }
  }

  // Initialize
  fetchStatus()

  return {
    theme,
    drawer,
    isRunning,
    status,
    toggleTheme,
    toggleDrawer,
    runBot,
    fetchStatus
  }
})