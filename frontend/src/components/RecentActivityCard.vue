<template>
  <v-card>
    <v-card-title class="text-subtitle-1 font-weight-bold">
      <v-icon start color="primary">mdi-history</v-icon>
      Recent Activity
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
    
    <v-list v-else-if="appStore.status.lastRun" lines="two">
      <v-list-item>
        <template v-slot:prepend>
          <v-avatar color="success" size="36">
            <v-icon color="white">mdi-check</v-icon>
          </v-avatar>
        </template>
        <v-list-item-title>RSS Feed Generated</v-list-item-title>
        <v-list-item-subtitle>
          {{ formatDateTime(appStore.status.lastRun) }}
        </v-list-item-subtitle>
      </v-list-item>
      <v-divider></v-divider>
      
      <v-list-item>
        <template v-slot:prepend>
          <v-avatar color="primary" size="36">
            <v-icon color="white">mdi-filter</v-icon>
          </v-avatar>
        </template>
        <v-list-item-title>Papers Filtered</v-list-item-title>
        <v-list-item-subtitle>
          {{ appStore.status.paperCount }} papers matched your filters
        </v-list-item-subtitle>
      </v-list-item>
      <v-divider></v-divider>
      
      <v-list-item v-if="appStore.status.papers && appStore.status.papers.length > 0">
        <template v-slot:prepend>
          <v-avatar color="info" size="36">
            <v-icon color="white">mdi-magnify</v-icon>
          </v-avatar>
        </template>
        <v-list-item-title>Keywords Matched</v-list-item-title>
        <v-list-item-subtitle>
          {{ uniqueKeywords.join(', ') }}
        </v-list-item-subtitle>
      </v-list-item>
    </v-list>
    
    <v-card-text v-else class="text-center py-4">
      <v-icon size="48" color="grey">mdi-alert-circle</v-icon>
      <p class="mt-2">No recent activity</p>
    </v-card-text>
  </v-card>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useAppStore } from '../stores/app'

export default {
  name: 'RecentActivityCard',
  props: {
    loading: {
      type: Boolean,
      default: false
    }
  },
  setup() {
    const appStore = useAppStore()
    
    // 提取所有唯一的关键词
    const uniqueKeywords = computed(() => {
      if (!appStore.status.papers || appStore.status.papers.length === 0) {
        return []
      }
      
      // 从所有论文中收集关键词并去重
      const keywordSet = new Set()
      appStore.status.papers.forEach(paper => {
        if (paper.keywords && paper.keywords.length) {
          paper.keywords.forEach(keyword => keywordSet.add(keyword))
        }
      })
      
      return Array.from(keywordSet)
    })
    
    // 格式化日期和时间
    const formatDateTime = (dateString) => {
      if (!dateString) return 'Unknown'
      
      try {
        // 解析ISO格式的日期字符串并使用用户本地时区显示
        const date = new Date(dateString)
        return new Intl.DateTimeFormat(navigator.language, {
          year: 'numeric',
          month: 'short',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          timeZoneName: 'short'
        }).format(date)
      } catch (e) {
        console.error('Error formatting date:', e)
        return dateString
      }
    }
    
    return {
      appStore,
      uniqueKeywords,
      formatDateTime
    }
  }
}
</script> 