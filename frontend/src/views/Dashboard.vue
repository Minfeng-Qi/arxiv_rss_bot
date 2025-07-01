<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="6" lg="4">
        <v-card height="100%">
          <v-card-title class="text-subtitle-1 font-weight-bold">
            <v-icon start color="primary">mdi-cog</v-icon>
            Configuration
          </v-card-title>
          <v-card-text>
            <v-list-item v-if="loading">
              <v-skeleton-loader type="list-item-two-line"></v-skeleton-loader>
            </v-list-item>
            <template v-else>
              <div class="d-flex align-center mb-2">
                <v-icon size="small" color="grey">mdi-magnify</v-icon>
                <span class="ml-2">Keywords: {{ keywordCount }}</span>
              </div>
              <div class="d-flex align-center mb-2">
                <v-icon size="small" color="grey">mdi-tag-multiple</v-icon>
                <span class="ml-2">Categories: {{ categoryCount }}</span>
              </div>
              <div class="d-flex align-center">
                <v-icon size="small" color="grey">mdi-calendar-range</v-icon>
                <span class="ml-2">Max Days Old: {{ maxDaysOld }}</span>
              </div>
            </template>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              variant="text"
              to="/config"
            >
              Edit Configuration
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="6" lg="4">
        <v-card height="100%">
          <v-card-title class="text-subtitle-1 font-weight-bold">
            <v-icon start color="primary">mdi-rss</v-icon>
            Latest Feed
          </v-card-title>
          <v-card-text>
            <v-list-item v-if="loading">
              <v-skeleton-loader type="list-item-two-line"></v-skeleton-loader>
            </v-list-item>
            <template v-else-if="appStore.status.lastFeed">
              <div class="d-flex align-center mb-2">
                <v-icon size="small" color="grey">mdi-file</v-icon>
                <span class="ml-2 text-truncate">{{ appStore.status.lastFeed }}</span>
              </div>
              <div class="d-flex align-center mb-2">
                <v-icon size="small" color="grey">mdi-calendar</v-icon>
                <span class="ml-2">{{ formatDateTime(appStore.status.lastRun) }}</span>
              </div>
              <div class="d-flex align-center">
                <v-icon size="small" color="grey">mdi-paper</v-icon>
                <span class="ml-2">{{ appStore.status.paperCount }} papers filtered</span>
              </div>
            </template>
            <div v-else class="text-center py-4">
              <v-icon size="32" color="grey">mdi-file-document-alert</v-icon>
              <p class="mt-2">No feeds generated yet</p>
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              variant="text"
              to="/feeds"
              :disabled="!appStore.status.lastFeed"
            >
              View Feeds
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="12" lg="4">
        <v-card height="100%">
          <v-card-title class="text-subtitle-1 font-weight-bold">
            <v-icon start color="primary">mdi-filter</v-icon>
            Papers Filtered
          </v-card-title>
          <v-card-text class="text-center">
            <v-skeleton-loader v-if="loading" type="image" height="120"></v-skeleton-loader>
            <template v-else>
              <div class="d-flex flex-column align-center justify-center" style="height: 120px">
                <span class="text-h2">{{ appStore.status.paperCount }}</span>
                <span class="text-subtitle-1">papers in latest feed</span>
              </div>
              <v-btn
                color="success"
                block
                class="mt-4"
                prepend-icon="mdi-play"
                :loading="appStore.isRunning"
                :disabled="appStore.isRunning"
                @click="runBot"
              >
                Run Now
              </v-btn>
            </template>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <v-row class="mt-4">
      <v-col cols="12" md="6">
        <recent-activity-card :loading="loading" />
      </v-col>
      
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="text-subtitle-1 font-weight-bold">
            <v-icon start color="primary">mdi-information</v-icon>
            System Information
          </v-card-title>
          <v-divider></v-divider>
          <v-list v-if="loading" lines="two">
            <v-list-item>
              <v-skeleton-loader type="list-item-avatar-two-line"></v-skeleton-loader>
            </v-list-item>
            <v-divider></v-divider>
            <v-list-item>
              <v-skeleton-loader type="list-item-avatar-two-line"></v-skeleton-loader>
            </v-list-item>
          </v-list>
          <v-list v-else lines="two">
            <v-list-item>
              <template v-slot:prepend>
                <v-icon color="primary">mdi-tag</v-icon>
              </template>
              <v-list-item-title>Keywords</v-list-item-title>
              <v-list-item-subtitle>
                {{ keywordList }}
              </v-list-item-subtitle>
            </v-list-item>
            
            <v-divider></v-divider>
            
            <v-list-item>
              <template v-slot:prepend>
                <v-icon color="primary">mdi-shape</v-icon>
              </template>
              <v-list-item-title>Categories</v-list-item-title>
              <v-list-item-subtitle>
                {{ categoryList }}
              </v-list-item-subtitle>
            </v-list-item>
            
            <v-divider></v-divider>
            
            <v-list-item>
              <template v-slot:prepend>
                <v-icon color="primary">mdi-filter</v-icon>
              </template>
              <v-list-item-title>Filter Settings</v-list-item-title>
              <v-list-item-subtitle>
                Max Results: {{ config.max_results }}, Max Days Old: {{ config.max_days_old }}
              </v-list-item-subtitle>
            </v-list-item>
            
            <v-divider></v-divider>
            
            <v-list-item>
              <template v-slot:prepend>
                <v-icon color="primary">mdi-clock-time-five</v-icon>
              </template>
              <v-list-item-title>Scheduling</v-list-item-title>
              <v-list-item-subtitle>
                {{ scheduleSummary }}
              </v-list-item-subtitle>
            </v-list-item>
            
            <v-divider></v-divider>
            
            <v-list-item>
              <template v-slot:prepend>
                <v-icon :color="subscriptionStatusColor">{{ subscriptionStatusIcon }}</v-icon>
              </template>
              <v-list-item-title>Email Subscription</v-list-item-title>
              <v-list-item-subtitle>
                {{ subscriptionStatusText }}
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useToast } from 'vue-toastification'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAppStore } from '../stores/app'
import RecentActivityCard from '../components/RecentActivityCard.vue'

export default {
  name: 'DashboardView',
  components: {
    RecentActivityCard
  },
  setup() {
    const router = useRouter()
    const toast = useToast()
    const appStore = useAppStore()
    
    const loading = ref(true)
    const config = ref({})
    
    // Computed values
    const keywordCount = computed(() => {
      return config.value.keywords?.length || 0
    })
    
    const keywordList = computed(() => {
      return config.value.keywords?.join(', ') || 'None configured'
    })
    
    const categoryCount = computed(() => {
      return config.value.categories?.length || 0
    })
    
    const categoryList = computed(() => {
      return config.value.categories?.join(', ') || 'None configured'
    })
    
    const maxDaysOld = computed(() => {
      return config.value.max_days_old || 30
    })
    
    const scheduleSummary = computed(() => {
      if (config.value.run_hour !== undefined && config.value.run_hour !== null) {
        return `Daily at ${config.value.run_hour}:00`
      }
      return 'Not scheduled'
    })
    
    // 邮件订阅状态
    const subscriptionStatusText = computed(() => {
      if (!config.value.email_subscription) {
        return 'Not enabled'
      }
      
      const emailConfig = config.value.email || {}
      if (!emailConfig.recipient) {
        return 'Enabled but no recipient configured'
      }
      
      return `Enabled (${emailConfig.recipient})`
    })
    
    const subscriptionStatusIcon = computed(() => {
      if (!config.value.email_subscription) {
        return 'mdi-email-off'
      }
      
      const emailConfig = config.value.email || {}
      if (!emailConfig.recipient || !emailConfig.smtp_server || !emailConfig.username || !emailConfig.password) {
        return 'mdi-email-alert'
      }
      
      return 'mdi-email-check'
    })
    
    const subscriptionStatusColor = computed(() => {
      if (!config.value.email_subscription) {
        return 'grey'
      }
      
      const emailConfig = config.value.email || {}
      if (!emailConfig.recipient || !emailConfig.smtp_server || !emailConfig.username || !emailConfig.password) {
        return 'warning'
      }
      
      return 'success'
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
    
    // Load configuration
    const loadConfig = async () => {
      try {
        const response = await axios.get('/api/config')
        if (response.data.success) {
          config.value = response.data.config
        }
      } catch (error) {
        toast.error('Failed to load configuration: ' + error.message)
      }
    }
    
    // Run bot
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
    
    let intervalId = null
    onMounted(async () => {
      loading.value = true
      try {
        await Promise.all([
          loadConfig(),
          appStore.fetchStatus()
        ])
        // 每30秒自动刷新Recent Activity
        intervalId = setInterval(() => {
          appStore.fetchStatus()
        }, 30000)
      } catch (error) {
        console.error('Error loading dashboard data:', error)
      } finally {
        loading.value = false
      }
    })
    onUnmounted(() => {
      if (intervalId) clearInterval(intervalId)
    })
    
    return {
      appStore,
      loading,
      config,
      keywordCount,
      keywordList,
      categoryCount,
      categoryList,
      maxDaysOld,
      scheduleSummary,
      subscriptionStatusText,
      subscriptionStatusIcon,
      subscriptionStatusColor,
      formatDateTime,
      runBot
    }
  }
}
</script>