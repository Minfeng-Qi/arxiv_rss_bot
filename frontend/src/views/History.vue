<template>
  <div class="history">
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon large class="mr-2">mdi-history</v-icon>
            历史记录
            <v-spacer></v-spacer>
            <v-select
              v-model="perPage"
              :items="[10, 20, 50]"
              label="每页条数"
              density="compact"
              class="ma-0 pa-0 history-select"
              style="max-width: 100px"
              hide-details
            ></v-select>
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="records"
              :loading="loading"
              hover
              class="history-table"
              :items-per-page="perPage"
            >
              <template v-slot:item.timestamp="{ item }">
                {{ formatDate(item.timestamp) }}
              </template>
              <template v-slot:item.keywords="{ item }">
                <v-chip-group>
                  <v-chip
                    v-for="(keyword, i) in item.keywords"
                    :key="i"
                    size="small"
                    color="primary"
                    variant="outlined"
                    class="text-caption"
                  >
                    {{ keyword }}
                  </v-chip>
                </v-chip-group>
              </template>
              <template v-slot:item.categories="{ item }">
                <v-chip-group>
                  <v-chip
                    v-for="(category, i) in item.categories"
                    :key="i"
                    size="small"
                    color="info"
                    variant="outlined"
                    class="text-caption"
                  >
                    {{ category }}
                  </v-chip>
                </v-chip-group>
              </template>
              <template v-slot:item.actions="{ item }">
                <v-tooltip text="查看详情">
                  <template v-slot:activator="{ props }">
                    <v-btn
                      v-bind="props"
                      icon="mdi-eye"
                      size="small"
                      variant="text"
                      @click="viewRecord(item)"
                    ></v-btn>
                  </template>
                </v-tooltip>
                <v-tooltip text="下载输出文件">
                  <template v-slot:activator="{ props }">
                    <v-btn
                      v-bind="props"
                      icon="mdi-download"
                      size="small"
                      variant="text"
                      @click="downloadRss(item)"
                      :disabled="!item.output_file"
                    ></v-btn>
                  </template>
                </v-tooltip>
              </template>
            </v-data-table>

            <div class="d-flex justify-center mt-4">
              <v-pagination
                v-model="page"
                :length="totalPages"
                @update:model-value="fetchHistory"
                rounded="circle"
              ></v-pagination>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 历史记录详情对话框 -->
    <v-dialog v-model="detailDialog" max-width="900">
      <v-card v-if="selectedRecord">
        <v-card-title class="d-flex align-center">
          <v-icon large class="mr-2">mdi-file-document</v-icon>
          历史记录详情
          <v-spacer></v-spacer>
          <v-btn icon="mdi-close" variant="text" @click="detailDialog = false"></v-btn>
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" sm="6">
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon>mdi-calendar</v-icon>
                </template>
                <v-list-item-title>创建时间</v-list-item-title>
                <v-list-item-subtitle>{{ formatDate(selectedRecord.timestamp) }}</v-list-item-subtitle>
              </v-list-item>
            </v-col>
            <v-col cols="12" sm="6">
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon>mdi-file-document-outline</v-icon>
                </template>
                <v-list-item-title>论文数量</v-list-item-title>
                <v-list-item-subtitle>{{ selectedRecord.papers_count }} 篇</v-list-item-subtitle>
              </v-list-item>
            </v-col>
            <v-col cols="12" sm="6">
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon>mdi-tag-multiple</v-icon>
                </template>
                <v-list-item-title>关键词</v-list-item-title>
                <v-list-item-subtitle>
                  <v-chip-group>
                    <v-chip
                      v-for="(keyword, i) in selectedRecord.config?.keywords"
                      :key="i"
                      size="small"
                      color="primary"
                      variant="outlined"
                      class="text-caption"
                    >
                      {{ keyword }}
                    </v-chip>
                  </v-chip-group>
                </v-list-item-subtitle>
              </v-list-item>
            </v-col>
            <v-col cols="12" sm="6">
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon>mdi-folder-multiple</v-icon>
                </template>
                <v-list-item-title>分类</v-list-item-title>
                <v-list-item-subtitle>
                  <v-chip-group>
                    <v-chip
                      v-for="(category, i) in selectedRecord.config?.categories"
                      :key="i"
                      size="small"
                      color="info"
                      variant="outlined"
                      class="text-caption"
                    >
                      {{ category }}
                    </v-chip>
                  </v-chip-group>
                </v-list-item-subtitle>
              </v-list-item>
            </v-col>
          </v-row>

          <v-divider class="my-4"></v-divider>

          <h3 class="mb-3">论文列表</h3>
          <v-expansion-panels v-if="selectedRecord.papers?.length">
            <v-expansion-panel
              v-for="(paper, i) in selectedRecord.papers"
              :key="i"
              :title="paper.title"
            >
              <template v-slot:text>
                <div class="paper-details">
                  <div class="mb-2">
                    <strong>作者:</strong> {{ paper.authors?.join(', ') || '未知' }}
                  </div>
                  <div class="mb-2">
                    <strong>机构:</strong> {{ paper.institutions?.join('; ') || '未知' }}
                  </div>
                  <div class="mb-2">
                    <strong>发布日期:</strong> {{ formatDate(paper.published) }}
                  </div>
                  <div class="mb-2">
                    <strong>匹配关键词:</strong>
                    <v-chip-group>
                      <v-chip
                        v-for="(keyword, j) in paper.matched_keywords"
                        :key="j"
                        size="small"
                        color="success"
                        class="text-caption"
                      >
                        {{ keyword }}
                      </v-chip>
                    </v-chip-group>
                  </div>
                  <div class="mb-2">
                    <strong>摘要:</strong>
                    <div class="mt-1 text-body-2">{{ paper.summary }}</div>
                  </div>
                  <v-btn
                    :href="paper.link"
                    target="_blank"
                    color="primary"
                    variant="outlined"
                    size="small"
                    prepend-icon="mdi-open-in-new"
                  >
                    在arXiv上查看
                  </v-btn>
                </div>
              </template>
            </v-expansion-panel>
          </v-expansion-panels>
          <v-alert
            v-else
            type="info"
            density="compact"
            variant="tonal"
            class="mt-4"
          >
            没有找到论文记录。
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            variant="tonal"
            @click="detailDialog = false"
          >
            关闭
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '@/services/api'
import { format } from 'date-fns'
import { useAppStore } from '@/store/app'

const appStore = useAppStore()

// 表格设置
const headers = [
  { title: '时间', key: 'timestamp', align: 'start', sortable: true },
  { title: '论文数量', key: 'papers_count', align: 'center', sortable: true },
  { title: '关键词', key: 'keywords', align: 'start', sortable: false },
  { title: '分类', key: 'categories', align: 'start', sortable: false },
  { title: '操作', key: 'actions', align: 'center', sortable: false },
]

// 数据和状态
const records = ref([])
const loading = ref(false)
const page = ref(1)
const perPage = ref(10)
const totalPages = ref(1)
const detailDialog = ref(false)
const selectedRecord = ref(null)

// 监听分页变化
watch(perPage, () => {
  page.value = 1 // 重置到第一页
  fetchHistory()
})

// 获取历史记录列表
const fetchHistory = async () => {
  loading.value = true
  try {
    const response = await api.get(`/history?page=${page.value}&per_page=${perPage.value}`)
    if (response.data.success) {
      records.value = response.data.records
      totalPages.value = response.data.pagination.total_pages
    } else {
      appStore.showSnackbar('获取历史记录失败', 'error')
    }
  } catch (error) {
    console.error('Error fetching history:', error)
    appStore.showSnackbar('获取历史记录时出错', 'error')
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知'
  try {
    return format(new Date(dateString), 'yyyy-MM-dd HH:mm:ss')
  } catch (e) {
    return dateString
  }
}

// 查看历史记录详情
const viewRecord = async (record) => {
  loading.value = true
  try {
    const response = await api.get(`/history/${record.id}`)
    if (response.data.success) {
      selectedRecord.value = response.data.record
      detailDialog.value = true
    } else {
      appStore.showSnackbar('获取历史记录详情失败', 'error')
    }
  } catch (error) {
    console.error('Error fetching history record:', error)
    appStore.showSnackbar('获取历史记录详情时出错', 'error')
  } finally {
    loading.value = false
  }
}

// 下载RSS文件
const downloadRss = async (record) => {
  if (!record.output_file) {
    appStore.showSnackbar('此记录没有关联的输出文件', 'warning')
    return
  }

  try {
    const response = await api.get(`/output/${record.output_file}`)
    if (response.data.success) {
      const blob = new Blob([response.data.content], { type: 'application/xml' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = record.output_file
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } else {
      appStore.showSnackbar('下载RSS文件失败', 'error')
    }
  } catch (error) {
    console.error('Error downloading RSS file:', error)
    appStore.showSnackbar('下载RSS文件时出错', 'error')
  }
}

// 初始化
onMounted(() => {
  fetchHistory()
})
</script>

<style scoped>
.history-select {
  width: 100px !important;
}

.history-table {
  margin-top: 16px;
}

.paper-details {
  padding: 8px 0;
}
</style> 