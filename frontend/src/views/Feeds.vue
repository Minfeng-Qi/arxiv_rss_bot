<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h4 d-flex align-center">
            <v-icon start size="large" color="primary">mdi-rss</v-icon>
            RSS Feeds
            <v-spacer></v-spacer>
            <v-select
              v-model="selectedFeed"
              :items="feedFiles"
              label="Select Feed"
              density="compact"
              style="max-width: 300px"
              variant="outlined"
              hide-details
              class="mt-2"
              item-title="title"
              item-value="value"
              :disabled="feedFiles.length === 0"
            ></v-select>
            <v-btn
              icon
              color="error"
              :disabled="!selectedFeed"
              @click="deleteFeedFile"
              class="ml-2"
            >
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </v-card-title>
          
          <v-divider></v-divider>
          
          <v-card-text v-if="loading">
            <v-skeleton-loader type="article,article,article"></v-skeleton-loader>
          </v-card-text>
          
          <v-card-text v-else-if="feedFiles.length === 0" class="text-center py-8">
            <v-icon size="64" color="grey" class="mb-4">mdi-file-document-alert</v-icon>
            <h3 class="text-h5 mb-2">No RSS Feeds Available</h3>
            <p class="text-body-1 mb-4">Run the bot to generate an RSS feed</p>
            <v-btn
              color="primary"
              prepend-icon="mdi-play"
              to="/"
            >
              Go to Dashboard
            </v-btn>
          </v-card-text>
          
          <div v-else>
            <!-- Feed metadata -->
            <v-card-text>
              <v-row>
                <v-col cols="12" md="6">
                  <v-list-item>
                    <template v-slot:prepend>
                      <v-icon color="primary">mdi-calendar</v-icon>
                    </template>
                    <v-list-item-title>Generation Date</v-list-item-title>
                    <v-list-item-subtitle>{{ formatDate(extractDateFromFilename(selectedFeed)) }}</v-list-item-subtitle>
                  </v-list-item>
                </v-col>
                <v-col cols="12" md="6">
                  <v-list-item>
                    <template v-slot:prepend>
                      <v-icon color="primary">mdi-file-link</v-icon>
                    </template>
                    <v-list-item-title>Feed URL</v-list-item-title>
                    <v-list-item-subtitle class="d-flex align-center">
                      <a :href="getFeedUrl()" target="_blank" class="text-truncate">{{ getFeedUrl() }}</a>
                      <v-btn icon size="small" @click="copyToClipboard(getFeedUrl())" class="ms-2">
                        <v-icon size="small">mdi-content-copy</v-icon>
                      </v-btn>
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-col>
              </v-row>
              
              <v-row class="mt-2">
                <v-col cols="12" class="d-flex justify-end">
                  <v-btn
                    color="primary"
                    variant="outlined"
                    prepend-icon="mdi-download"
                    @click="downloadFeed"
                    size="small"
                    class="mr-2"
                  >
                    Download RSS
                  </v-btn>
                  <v-btn
                    color="secondary"
                    variant="outlined"
                    prepend-icon="mdi-refresh"
                    @click="refreshFeed"
                    size="small"
                    :loading="refreshing"
                  >
                    Refresh
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-text>
            
            <v-divider></v-divider>
            
            <!-- Paper list -->
            <v-card-text v-if="papers.length > 0">
              <div class="d-flex align-center justify-space-between mb-4">
                <h3 class="text-h6">Papers ({{ papers.length }})</h3>
                <div class="d-flex align-center">
                  <v-select
                    v-model="pageSize"
                    :items="[5, 10, 20, 50]"
                    label="Papers per page"
                    density="compact"
                    style="width: 150px"
                    variant="outlined"
                    hide-details
                  ></v-select>
                </div>
              </div>
              
              <v-card v-for="(paper, index) in paginatedPapers" :key="index" class="mb-4" variant="outlined">
                <v-card-title class="text-subtitle-1 font-weight-bold" v-html="highlightKeywords(paper.title, paper.keywords)"></v-card-title>
                
                <v-card-text>
                  <!-- 高亮关键词 -->
                  <div v-if="paper.keywords && paper.keywords.length" class="d-flex align-center flex-wrap mb-2">
                    <v-chip
                      v-for="(kw, idx) in paper.keywords"
                      :key="`kw-${idx}`"
                      color="success"
                      variant="elevated"
                      class="mr-1 mb-1"
                      size="small"
                    >
                      <v-icon start size="x-small">mdi-magnify</v-icon>
                      <span class="font-weight-bold">{{ kw }}</span>
                    </v-chip>
                  </div>
                  
                  <v-chip-group>
                    <v-chip v-for="(cat, idx) in paper.categories" :key="idx" size="small" color="info" variant="outlined">
                      {{ cat }}
                    </v-chip>
                  </v-chip-group>
                  
                  <div class="d-flex align-center mt-2">
                    <v-icon color="grey" size="small">mdi-account-multiple</v-icon>
                    <span class="ms-2">{{ paper.authors.join(', ') }}</span>
                  </div>
                  
                  <div v-if="paper.institutions && paper.institutions.length" class="d-flex align-center mt-2">
                    <v-icon color="grey" size="small">mdi-domain</v-icon>
                    <span class="ms-2">{{ paper.institutions.join('; ') }}</span>
                  </div>
                  
                  <div class="d-flex align-center mt-2">
                    <v-icon color="grey" size="small">mdi-calendar</v-icon>
                    <span class="ms-2">{{ formatDate(paper.pubDate) }}</span>
                  </div>
                  
                  <div class="d-flex align-center mt-2">
                    <v-btn
                      icon
                      @click="toggleAbstract(index)"
                      :aria-label="expandedAbstracts.has(index) ? '收起摘要' : '展开摘要'"
                      size="small"
                    >
                      <v-icon>
                        {{ expandedAbstracts.has(index) ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
                      </v-icon>
                    </v-btn>
                    <span class="ml-2">Abstract</span>
                  </div>
                  <v-expand-transition>
                    <div v-if="expandedAbstracts.has(index)" class="mt-2" style="white-space: pre-line;" v-html="highlightKeywords(paper.abstract, paper.keywords)"></div>
                  </v-expand-transition>
                </v-card-text>
                
                <v-card-actions>
                  <v-btn
                    variant="tonal"
                    color="primary"
                    size="small"
                    :href="paper.link"
                    target="_blank"
                    prepend-icon="mdi-file-pdf-box"
                  >
                    PDF
                  </v-btn>
                  <v-btn
                    variant="tonal"
                    color="secondary"
                    size="small"
                    :href="paper.link.replace('/pdf/', '/abs/')"
                    target="_blank"
                    prepend-icon="mdi-information"
                  >
                    Abstract
                  </v-btn>
                </v-card-actions>
              </v-card>
              
              <!-- Pagination -->
              <div class="d-flex justify-center mt-4">
                <v-pagination
                  v-model="page"
                  :length="totalPages"
                  :total-visible="7"
                  @update:model-value="updatePage"
                ></v-pagination>
              </div>
            </v-card-text>
            
            <!-- No papers found -->
            <v-card-text v-else class="text-center py-6">
              <v-icon size="48" color="grey">mdi-file-search</v-icon>
              <p class="mt-2">No papers found in this feed</p>
            </v-card-text>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref, watch, onMounted, computed } from 'vue'
import { useToast } from 'vue-toastification'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { format, parseISO } from 'date-fns'
import { useAppStore } from '../stores/app'

export default {
  name: 'FeedsView',
  setup() {
    const toast = useToast()
    const route = useRoute()
    const router = useRouter()
    const appStore = useAppStore()
    
    const loading = ref(true)
    const refreshing = ref(false)
    const feedFiles = ref([])
    const selectedFeed = ref('')
    const feedContent = ref('')
    const papers = ref([])
    const pageSize = ref(5)
    const page = ref(1)
    const totalPages = ref(1)
    const expandedAbstracts = ref(new Set())
    
    // Load feed files
    const loadFeedFiles = async () => {
      try {
        loading.value = true
        const response = await axios.get('/api/output')
        const files = response.data.files || []
        
        // 确保没有获取到文件列表时显示正确
        if (files.length === 0) {
          feedFiles.value = []
          loading.value = false
          return
        }
        
        // 为每个文件添加一个更友好的显示名称
        feedFiles.value = files.map(file => {
          const date = extractDateFromFilename(file)
          const formattedDate = formatDate(date)
          return {
            value: file,
            title: `${formattedDate} (${file})`
          }
        })
        
        // 按日期排序，最新的在前面
        feedFiles.value.sort((a, b) => {
          const dateA = extractDateFromFilename(a.value)
          const dateB = extractDateFromFilename(b.value)
          return dateB.getTime() - dateA.getTime()
        })
        
        // 从URL参数中或默认选择第一个feed
        if (route.query.file && feedFiles.value.some(f => f.value === route.query.file)) {
          selectedFeed.value = route.query.file
        } else if (feedFiles.value.length > 0) {
          selectedFeed.value = feedFiles.value[0].value
        }
        
        // Load the selected feed
        if (selectedFeed.value) {
          await loadFeedContent()
        } else {
          loading.value = false
        }
      } catch (error) {
        console.error('Error loading feed list:', error)
        toast.error('Error loading feed list: ' + error.message)
        loading.value = false
      }
    }
    
    // Load feed content
    const loadFeedContent = async () => {
      if (!selectedFeed.value) return
      
      try {
        loading.value = true
        const response = await axios.get(`/api/output/${selectedFeed.value}`)
        feedContent.value = response.data.content
        parseFeed()
        loading.value = false
        
        // Update URL query param
        if (route.query.file !== selectedFeed.value) {
          router.replace({ query: { file: selectedFeed.value }})
        }
      } catch (error) {
        toast.error('Error loading feed content: ' + error.message)
        loading.value = false
      }
    }
    
    // Refresh feed list and content
    const refreshFeed = async () => {
      refreshing.value = true
      try {
        // 触发新的运行并生成新记录
        const runResponse = await axios.post('/api/run')
        if (runResponse.data.success) {
          // 如果运行成功并生成了新文件
          if (runResponse.data.result && runResponse.data.result.output_file) {
            toast.success(`生成了 ${runResponse.data.result.papers_count} 篇论文`)
            
            // 重新加载feed列表
            await loadFeedFiles()
            
            // 自动选择新生成的feed
            const newFile = runResponse.data.result.output_file
            if (feedFiles.value.some(f => f.value === newFile)) {
              selectedFeed.value = newFile
              await loadFeedContent()
            }
            await appStore.fetchStatus()
          } else {
            toast.info(runResponse.data.message || '没有找到新论文')
            await loadFeedFiles() // 仍然刷新列表
          }
        } else {
          toast.error(runResponse.data.message || '流水线运行失败')
        }
      } catch (error) {
        toast.error('刷新Feed出错: ' + error.message)
      } finally {
        refreshing.value = false
      }
    }
    
    // Download current feed
    const downloadFeed = () => {
      if (!feedContent.value || !selectedFeed.value) {
        toast.warning('No feed content to download')
        return
      }
      
      const blob = new Blob([feedContent.value], { type: 'application/xml' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = selectedFeed.value
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      toast.success('RSS feed downloaded')
    }
    
    // Parse RSS XML content to extract papers
    const parseFeed = () => {
      try {
        const parser = new DOMParser()
        const xmlDoc = parser.parseFromString(feedContent.value, "text/xml")
        const items = xmlDoc.getElementsByTagName("item")
        const parsedPapers = []
        
        for (let i = 0; i < items.length; i++) {
          const item = items[i]
          
          // Parse title and link
          const title = item.getElementsByTagName("title")[0]?.textContent || 'Untitled'
          const link = item.getElementsByTagName("link")[0]?.textContent || ''
          const pubDateElement = item.getElementsByTagName("pubDate")[0]
          const pubDate = pubDateElement ? new Date(pubDateElement.textContent) : new Date()
          
          // Parse description for categories, keywords, authors, institutions
          const description = item.getElementsByTagName("description")[0]?.textContent || ''
          const categories = Array.from(item.getElementsByTagName("category")).map(cat => cat.textContent)
          
          // Parse authors and institutions from description
          let authors = []
          let institutions = []
          let keywords = []
          let abstract = ''
          
          // 提取匹配的关键词
          const keywordsMatch = description.match(/Matched keywords:\s*(.*?)(?:\.|\n|$)/i)
          if (keywordsMatch && keywordsMatch[1]) {
            keywords = keywordsMatch[1].split(', ').map(kw => kw.trim())
          }
          
          // 提取作者
          const authorsMatch = description.match(/Authors:\s*(.*?)(?:\.|\n|$)/i)
          if (authorsMatch && authorsMatch[1]) {
            authors = authorsMatch[1].split(', ').map(a => a.trim())
            // 如果描述中没有找到作者，从RSS的author标签中提取
            const authorElements = item.getElementsByTagName("author")
            for (let j = 0; j < authorElements.length; j++) {
              const authorName = authorElements[j].textContent.trim()
              if (authorName && !authors.includes(authorName)) {
                authors.push(authorName)
              }
            }
          }
          
          // 提取机构
          const instMatch = description.match(/Institutions:\s*(.*?)(?:\.|\n|$)/i)
          if (instMatch && instMatch[1]) {
            institutions = instMatch[1].split('; ').map(i => i.trim())
          }
          
          // 提取摘要正文（去掉前面的Categories/Matched keywords/Authors/Institutions等头部）
          // 只保留最后一段正文
          const abstractMatch = description.match(/(?:Authors:.*?(?:\.|\n|$))([\s\S]*)/i)
          if (abstractMatch && abstractMatch[1]) {
            abstract = abstractMatch[1].trim()
          } else {
            // 如果没有Authors字段，尝试从Matched keywords后截取
            const altAbstractMatch = description.match(/(?:Matched keywords:.*?(?:\.|\n|$))([\s\S]*)/i)
            if (altAbstractMatch && altAbstractMatch[1]) {
              abstract = altAbstractMatch[1].trim()
            } else {
              // 否则直接用description
              abstract = description.trim()
            }
          }
          
          parsedPapers.push({
            title,
            link,
            pubDate,
            description,
            abstract,
            categories,
            keywords,
            authors,
            institutions
          })
        }
        
        // 按照发布日期降序排序（最新的在前面）
        papers.value = parsedPapers.sort((a, b) => {
          return b.pubDate.getTime() - a.pubDate.getTime()
        })
        
        // Calculate total pages
        totalPages.value = Math.ceil(papers.value.length / pageSize.value)
        
        // Update paginated papers
        updatePage()
      } catch (error) {
        console.error('Error parsing feed:', error)
        toast.error('Error parsing feed content')
        papers.value = []
      }
    }
    
    // Extract date from filename
    const extractDateFromFilename = (filename) => {
      // 新格式：20250701_144331_RL.xml 或 20250701_144331.xml
      let match = filename.match(/^(\d{8})_(\d{6})(?:_\w+)?\.xml$/)
      if (match) {
        const year = parseInt(match[1].slice(0, 4))
        const month = parseInt(match[1].slice(4, 6)) - 1
        const day = parseInt(match[1].slice(6, 8))
        const hour = parseInt(match[2].slice(0, 2))
        const minute = parseInt(match[2].slice(2, 4))
        const second = parseInt(match[2].slice(4, 6))
        return new Date(year, month, day, hour, minute, second)
      }
      // 兼容旧格式 arxiv_filtered_20250701_133243.xml
      match = filename.match(/arxiv_filtered_(\d{4})(\d{2})(\d{2})(?:_(\d{2})(\d{2})(\d{2}))?\.xml/)
      if (match) {
        const year = parseInt(match[1])
        const month = parseInt(match[2]) - 1
        const day = parseInt(match[3])
        if (match[4]) {
          const hour = parseInt(match[4])
          const minute = parseInt(match[5])
          const second = parseInt(match[6])
          return new Date(year, month, day, hour, minute, second)
        }
        return new Date(year, month, day, 12, 0, 0)
      }
      return new Date()
    }
    
    // Format date
    const formatDate = (date) => {
      if (!date || isNaN(date.getTime())) {
        return 'Unknown date'
      }
      
      // 使用用户本地时区格式化日期，显示精确时间和时区
      try {
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
        // 回退到简单格式
        return date.toLocaleString()
      }
    }
    
    // Get feed URL for sharing
    const getFeedUrl = () => {
      if (!selectedFeed.value) return ''
      const base = window.location.origin
      return `${base}/api/output/${selectedFeed.value}`
    }
    
    // Copy feed URL to clipboard
    const copyToClipboard = (text) => {
      navigator.clipboard.writeText(text).then(() => {
        toast.success('Feed URL copied to clipboard')
      }).catch(() => {
        toast.error('Failed to copy URL')
      })
    }
    
    // Watch for selected feed changes
    watch(selectedFeed, async () => {
      if (selectedFeed.value) {
        await loadFeedContent()
      }
    })
    
    // Load feeds on mount
    onMounted(loadFeedFiles)
    
    // Calculate paginated papers
    const paginatedPapers = computed(() => {
      const start = (page.value - 1) * pageSize.value
      const end = start + pageSize.value
      return papers.value.slice(start, end)
    })
    
    // Update page
    const updatePage = () => {
      page.value = Math.min(Math.max(page.value, 1), totalPages.value)
    }
    
    function toggleAbstract(index) {
      if (expandedAbstracts.value.has(index)) {
        expandedAbstracts.value.delete(index)
      } else {
        expandedAbstracts.value.add(index)
      }
    }
    
    function highlightKeywords(text, keywords) {
      if (!keywords || keywords.length === 0 || !text) return text
      // 按长度降序，优先长短语
      const sortedKeywords = [...keywords].sort((a, b) => b.length - a.length)
      let result = text
      sortedKeywords.forEach(kw => {
        if (!kw) return
        const isPhrase = kw.trim().split(/\s+/).length > 1
        const pattern = isPhrase
          ? new RegExp(kw.replace(/[.*+?^${}()|[\\]\\]/g, '\\$&'), 'gi')
          : new RegExp(`\\b${kw.replace(/[.*+?^${}()|[\\]\\]/g, '\\$&')}\\b`, 'gi')
        result = result.replace(pattern, '<span class="highlight">$&</span>')
      })
      return result
    }
    
    const deleteFeedFile = async () => {
      if (!selectedFeed.value) return
      if (!window.confirm('Are you sure you want to delete this feed file?')) return
      try {
        const resp = await axios.delete(`/api/output/${selectedFeed.value}`)
        if (resp.data.success) {
          toast.success('Feed file deleted')
          await loadFeedFiles()
        } else {
          toast.error(resp.data.error || 'Delete failed')
        }
      } catch (e) {
        toast.error('Delete failed: ' + e.message)
      }
    }
    
    return {
      loading,
      refreshing,
      feedFiles,
      selectedFeed,
      papers,
      pageSize,
      page,
      totalPages,
      loadFeedFiles,
      loadFeedContent,
      refreshFeed,
      downloadFeed,
      extractDateFromFilename,
      formatDate,
      getFeedUrl,
      copyToClipboard,
      paginatedPapers,
      updatePage,
      expandedAbstracts,
      toggleAbstract,
      highlightKeywords,
      deleteFeedFile
    }
  }
}
</script>

<style scoped>
.highlight {
  background: #ffe082 !important;
  color: #d84315 !important;
  border-radius: 4px;
  padding: 0 2px;
  font-weight: bold;
  transition: background 0.2s;
}
</style>