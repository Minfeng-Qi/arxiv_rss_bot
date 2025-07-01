<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h4 d-flex align-center">
            <v-icon start size="large" color="primary">mdi-cog</v-icon>
            Configuration
            <v-spacer></v-spacer>
            <v-btn
              color="success"
              prepend-icon="mdi-content-save"
              @click="saveConfig"
              :loading="isSaving"
            >
              Save Changes
            </v-btn>
          </v-card-title>
        
          <v-card-text v-if="loading">
            <v-skeleton-loader type="article"></v-skeleton-loader>
          </v-card-text>
        
          <v-form v-else ref="form" @submit.prevent="saveConfig">
            <v-card-text>
              <v-expansion-panels v-model="expandedPanels" multiple>
                <!-- Keywords -->
                <v-expansion-panel>
                  <v-expansion-panel-title>
                    <v-icon start color="primary">mdi-magnify</v-icon>
                    Keywords
                  </v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <p class="text-subtitle-1 mb-2">Enter the keywords for filtering papers (one keyword per line)</p>
                    <v-textarea
                      v-model="keywordsText"
                      variant="outlined"
                      placeholder="machine learning&#10;neural network&#10;deep learning"
                      rows="5"
                      hint="Papers matching these keywords will be included in the feed"
                      persistent-hint
                    ></v-textarea>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              
                <!-- ArXiv Categories -->
                <v-expansion-panel>
                  <v-expansion-panel-title>
                    <v-icon start color="primary">mdi-tag-multiple</v-icon>
                    Categories
                  </v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <p class="text-subtitle-1 mb-2">Select arXiv categories to include</p>
                    <v-row>
                      <v-col cols="12" md="6" lg="4" v-for="(category, idx) in categoriesDisplay" :key="idx">
                        <div 
                          class="pa-2 category-select d-flex align-center" 
                          :class="{'selected': isCategorySelected(category.code)}"
                          @click="manualToggleCategory(category.code)"
                          style="border-radius: 4px; cursor: pointer;"
                        >
                          <v-icon 
                            :color="isCategorySelected(category.code) ? 'primary' : 'grey'" 
                            class="mr-2"
                          >
                            {{ isCategorySelected(category.code) ? 'mdi-checkbox-marked' : 'mdi-checkbox-blank-outline' }}
                          </v-icon>
                          <div>
                            <strong>{{ category.code }}</strong>
                            <div class="text-caption text-grey">{{ category.name }}</div>
                          </div>
                        </div>
                      </v-col>
                    </v-row>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              
                <!-- Filter Parameters -->
                <v-expansion-panel>
                  <v-expansion-panel-title>
                    <v-icon start color="primary">mdi-filter</v-icon>
                    Filter Parameters
                  </v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <v-row>
                      <v-col cols="12" md="6">
                        <v-text-field
                          v-model.number="config.max_results"
                          label="Maximum Results"
                          type="number"
                          min="1"
                          max="100"
                          variant="outlined"
                          hint="Number of papers to include in RSS feed"
                          persistent-hint
                        ></v-text-field>
                      </v-col>
                      <v-col cols="12" md="6">
                        <v-text-field
                          v-model.number="config.max_days_old"
                          label="Maximum Days Old"
                          type="number"
                          min="1"
                          max="365"
                          variant="outlined"
                          hint="Only include papers published within this many days"
                          persistent-hint
                        ></v-text-field>
                      </v-col>
                    </v-row>
                  </v-expansion-panel-text>
                </v-expansion-panel>

                <!-- Date Range Filter -->
                <v-expansion-panel>
                  <v-expansion-panel-title>
                    <v-icon start color="primary">mdi-calendar-range</v-icon>
                    Date Range Filter
                  </v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <v-row>
                      <v-col cols="12" md="6">
                        <v-switch
                          v-model="enableDateRange"
                          color="primary"
                          label="Enable Date Range Filtering"
                          hint="Filter papers by specific year/month"
                          persistent-hint
                        ></v-switch>
                      </v-col>
                    </v-row>
                    
                    <v-row v-if="enableDateRange">
                      <v-col cols="12" md="6">
                        <v-select
                          v-model="dateRange.year"
                          :items="yearOptions"
                          label="Year"
                          variant="outlined"
                          clearable
                        ></v-select>
                      </v-col>
                      <v-col cols="12" md="6">
                        <v-select
                          v-model="dateRange.month"
                          :items="monthOptions"
                          label="Month"
                          variant="outlined"
                          clearable
                        ></v-select>
                      </v-col>
                    </v-row>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              
                <!-- Scheduling -->
                <v-expansion-panel>
                  <v-expansion-panel-title>
                    <v-icon start color="primary">mdi-clock-time-five</v-icon>
                    Scheduling
                  </v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <v-row>
                      <v-col cols="12" md="6">
                        <v-text-field
                          v-model.number="config.run_hour"
                          label="Daily Run Hour"
                          type="number"
                          min="0"
                          max="23"
                          variant="outlined"
                          hint="Hour of day to run (0-23, leave empty to disable scheduling)"
                          persistent-hint
                          clearable
                        ></v-text-field>
                      </v-col>
                    </v-row>
                  </v-expansion-panel-text>
                </v-expansion-panel>

                <!-- Notifications -->
                <v-expansion-panel>
                  <v-expansion-panel-title>
                    <v-icon start color="primary">mdi-email</v-icon>
                    Notifications
                  </v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <v-row>
                      <v-col cols="12" md="6">
                        <v-switch
                          v-model="config.email_on_error"
                          color="primary"
                          label="Email on Error"
                          hint="Receive email notifications when errors occur"
                          persistent-hint
                        ></v-switch>
                      </v-col>
                      <v-col cols="12" md="6" v-if="config.email_on_error">
                        <v-text-field
                          v-model="config.email_address"
                          label="Email Address"
                          variant="outlined"
                          placeholder="your@email.com"
                          hint="Email address for notifications"
                          persistent-hint
                        ></v-text-field>
                      </v-col>
                    </v-row>
                  </v-expansion-panel-text>
                </v-expansion-panel>
                
                <!-- Email Subscription -->
                <v-expansion-panel>
                  <v-expansion-panel-title>
                    <v-icon start color="primary">mdi-email-newsletter</v-icon>
                    Email Subscription
                  </v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <v-row>
                      <v-col cols="12" md="6">
                        <v-switch
                          v-model="config.email_subscription"
                          color="primary"
                          label="Enable Email Subscription"
                          hint="Automatically send new papers via email"
                          persistent-hint
                        ></v-switch>
                      </v-col>
                    </v-row>
                    
                    <v-row v-if="config.email_subscription">
                      <v-col cols="12">
                        <v-card variant="outlined" class="pa-3 mb-3">
                          <v-card-title class="text-subtitle-1">SMTP Settings</v-card-title>
                          <v-row>
                            <v-col cols="12" md="6">
                              <v-text-field
                                v-model="emailConfig.smtp_server"
                                label="SMTP Server"
                                variant="outlined"
                                placeholder="smtp.gmail.com"
                                hint="SMTP server address"
                                persistent-hint
                              ></v-text-field>
                            </v-col>
                            <v-col cols="12" md="6">
                              <v-text-field
                                v-model.number="emailConfig.port"
                                label="Port"
                                variant="outlined"
                                type="number"
                                placeholder="587"
                                hint="SMTP server port"
                                persistent-hint
                              ></v-text-field>
                            </v-col>
                            <v-col cols="12" md="6">
                              <v-text-field
                                v-model="emailConfig.username"
                                label="Username"
                                variant="outlined"
                                placeholder="your@email.com"
                                hint="SMTP username"
                                persistent-hint
                              ></v-text-field>
                            </v-col>
                            <v-col cols="12" md="6">
                              <v-text-field
                                v-model="emailConfig.password"
                                label="Password"
                                variant="outlined"
                                type="password"
                                placeholder="********"
                                hint="SMTP password or app password"
                                persistent-hint
                              ></v-text-field>
                            </v-col>
                          </v-row>
                        </v-card>
                      </v-col>
                      
                      <v-col cols="12">
                        <v-text-field
                          v-model="emailConfig.recipient"
                          label="Recipient Email"
                          variant="outlined"
                          placeholder="recipient@email.com"
                          hint="Email address to receive paper updates"
                          persistent-hint
                        ></v-text-field>
                      </v-col>
                      
                      <v-col cols="12">
                        <v-btn
                          color="info"
                          prepend-icon="mdi-email-check"
                          @click="testEmailConfig"
                          :loading="isTestingEmail"
                          class="mb-4"
                        >
                          Test Email Configuration
                        </v-btn>
                      </v-col>
                      
                      <v-col cols="12">
                        <v-alert type="info" variant="tonal" class="mb-0">
                          <p><strong>Note:</strong> The system keeps track of sent papers to avoid duplicates.</p>
                          <p>Subscription history is stored in <code>subscription_history.json</code> file.</p>
                        </v-alert>
                      </v-col>
                    </v-row>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </v-card-text>

            <v-divider></v-divider>

            <v-card-actions>
              <v-btn
                color="error"
                variant="text"
                prepend-icon="mdi-refresh"
                @click="resetForm"
              >
                Reset Changes
              </v-btn>
              <v-spacer></v-spacer>
              <v-btn
                color="success"
                prepend-icon="mdi-content-save"
                @click="saveConfig"
                :loading="isSaving"
              >
                Save Changes
              </v-btn>
            </v-card-actions>
          </v-form>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'
import axios from 'axios'

export default {
  name: 'ConfigView',
  setup() {
    const toast = useToast()
    const form = ref(null)
    const loading = ref(true)
    const isSaving = ref(false)
    const isTestingEmail = ref(false)
    const expandedPanels = ref([0]) // First panel expanded by default
    const enableDateRange = ref(false)
    
    // Form data
    const config = ref({
      keywords: [],
      categories: [],
      max_results: 10,
      max_days_old: 30,
      run_hour: null,
      email_on_error: false,
      email_address: '',
      date_range: null,
      email_subscription: false,
      email: {}
    })
    
    const originalConfig = ref({}) // For reset functionality
    const keywordsText = ref('')
    const selectedCategories = ref([])
    const dateRange = ref({
      year: null,
      month: null
    })
    
    // 邮件配置
    const emailConfig = ref({
      smtp_server: '',
      port: 587,
      username: '',
      password: '',
      recipient: ''
    })

    // ArXiv categories
    const categoriesDisplay = [
      { code: 'cs.AI', name: 'Artificial Intelligence'},
      { code: 'cs.AR', name: 'Hardware Architecture'},
      { code: 'cs.CC', name: 'Computational Complexity'},
      { code: 'cs.CE', name: 'Computational Engineering, Finance, and Science'},
      { code: 'cs.CG', name: 'Computational Geometry'},
      { code: 'cs.CL', name: 'Computation and Language'},
      { code: 'cs.CR', name: 'Cryptography and Security'},
      { code: 'cs.CV', name: 'Computer Vision and Pattern Recognition'},
      { code: 'cs.CY', name: 'Computers and Society'},
      { code: 'cs.DB', name: 'Databases'},
      { code: 'cs.DC', name: 'Distributed, Parallel, and Cluster Computing'},
      { code: 'cs.DL', name: 'Digital Libraries'},
      { code: 'cs.DM', name: 'Discrete Mathematics'},
      { code: 'cs.DS', name: 'Data Structures and Algorithms'},
      { code: 'cs.ET', name: 'Emerging Technologies'},
      { code: 'cs.FL', name: 'Formal Languages and Automata Theory'},
      { code: 'cs.GL', name: 'General Literature'},
      { code: 'cs.GR', name: 'Graphics'},
      { code: 'cs.GT', name: 'Computer Science and Game Theory'},
      { code: 'cs.HC', name: 'Human-Computer Interaction'},
      { code: 'cs.IR', name: 'Information Retrieval'},
      { code: 'cs.IT', name: 'Information Theory'},
      { code: 'cs.LG', name: 'Machine Learning'},
      { code: 'cs.LO', name: 'Logic in Computer Science'},
      { code: 'cs.MA', name: 'Multiagent Systems'},
      { code: 'cs.MM', name: 'Multimedia'},
      { code: 'cs.MS', name: 'Mathematical Software'},
      { code: 'cs.NA', name: 'Numerical Analysis'},
      { code: 'cs.NE', name: 'Neural and Evolutionary Computing'},
      { code: 'cs.NI', name: 'Networking and Internet Architecture'},
      { code: 'cs.OS', name: 'Operating Systems'},
      { code: 'cs.PF', name: 'Performance'},
      { code: 'cs.PL', name: 'Programming Languages'},
      { code: 'cs.RO', name: 'Robotics'},
      { code: 'cs.SC', name: 'Symbolic Computation'},
      { code: 'cs.SD', name: 'Sound'},
      { code: 'cs.SE', name: 'Software Engineering'},
      { code: 'cs.SI', name: 'Social and Information Networks'},
      { code: 'cs.SY', name: 'Systems and Control'},
      // Add other major categories like math, physics, etc. as needed
    ]

    // Generate year options (current year and past 5 years)
    const currentYear = new Date().getFullYear()
    const yearOptions = Array.from({ length: 6 }, (_, i) => ({
      title: currentYear - i,
      value: currentYear - i
    }))

    // Generate month options
    const monthNames = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ]
    const monthOptions = monthNames.map((name, idx) => ({
      title: name,
      value: idx + 1
    }))

    // Map between form data and config object
    const updateFormFromConfig = () => {
      keywordsText.value = config.value.keywords?.join('\n') || ''
      selectedCategories.value = config.value.categories || []
      
      if (config.value.date_range) {
        enableDateRange.value = true
        dateRange.value = { ...config.value.date_range }
      } else {
        enableDateRange.value = false
        dateRange.value = { year: null, month: null }
      }
      
      // 加载邮件配置
      if (config.value.email) {
        emailConfig.value = {
          smtp_server: config.value.email.smtp_server || '',
          port: config.value.email.port || 587,
          username: config.value.email.username || '',
          password: config.value.email.password || '',
          recipient: config.value.email.recipient || ''
        }
      }
      
      // Store original for reset
      originalConfig.value = JSON.parse(JSON.stringify(config.value))
    }

    const updateConfigFromForm = () => {
      // Parse keywords from text
      config.value.keywords = keywordsText.value
        .split('\n')
        .map(k => k.trim())
        .filter(k => k !== '')
      
      // Update categories
      config.value.categories = [...selectedCategories.value]
      
      // Update date range
      if (enableDateRange.value) {
        config.value.date_range = { ...dateRange.value }
      } else {
        config.value.date_range = null
      }
      
      // 更新邮件配置
      config.value.email = { ...emailConfig.value }
    }

    // 检查类别是否被选中
    const isCategorySelected = (code) => {
      return selectedCategories.value.includes(code)
    }
    
    // 切换类别选中状态
    const toggleCategory = (code) => {
      const index = selectedCategories.value.indexOf(code)
      if (index === -1) {
        selectedCategories.value.push(code)
      } else {
        selectedCategories.value.splice(index, 1)
      }
    }
    
    // 手动处理类别切换，添加调试日志
    const manualToggleCategory = (code) => {
      console.log('Toggle category:', code)
      console.log('Before:', [...selectedCategories.value])
      
      const index = selectedCategories.value.indexOf(code)
      if (index === -1) {
        selectedCategories.value.push(code)
      } else {
        selectedCategories.value.splice(index, 1)
      }
      
      console.log('After:', [...selectedCategories.value])
    }

    // Watch for changes in the date range switch
    watch(enableDateRange, (newVal) => {
      if (!newVal) {
        dateRange.value = { year: null, month: null }
      }
    })

    // Fetch config from server
    const fetchConfig = async () => {
      try {
        loading.value = true
        const response = await axios.get('/api/config')
        config.value = response.data.config
        updateFormFromConfig()
      } catch (error) {
        toast.error('Failed to load configuration: ' + error.message)
      } finally {
        loading.value = false
      }
    }

    // Save config to server
    const saveConfig = async () => {
      try {
        updateConfigFromForm()
        isSaving.value = true
        
        const response = await axios.post('/api/config', {
          config: config.value
        })
        
        if (response.data.success) {
          toast.success('Configuration saved successfully')
          // Update original config for reset
          originalConfig.value = JSON.parse(JSON.stringify(config.value))
        } else {
          toast.error('Failed to save configuration')
        }
      } catch (error) {
        toast.error('Error: ' + (error.response?.data?.error || error.message))
      } finally {
        isSaving.value = false
      }
    }

    // Reset form to original values
    const resetForm = () => {
      config.value = JSON.parse(JSON.stringify(originalConfig.value))
      updateFormFromConfig()
      toast.info('Form reset to last saved values')
    }
    
    // 测试邮件配置
    const testEmailConfig = async () => {
      try {
        // 检查必要的字段
        const requiredFields = ['smtp_server', 'port', 'username', 'password', 'recipient']
        const missingFields = requiredFields.filter(field => !emailConfig.value[field])
        
        if (missingFields.length > 0) {
          toast.error(`Missing required fields: ${missingFields.join(', ')}`)
          return
        }
        
        isTestingEmail.value = true
        const response = await axios.post('/api/email/test', {
          email_config: emailConfig.value
        })
        
        if (response.data.success) {
          toast.success(response.data.message || 'Test email sent successfully')
        } else {
          toast.error(`Failed to send test email: ${response.data.error}`)
        }
      } catch (error) {
        toast.error(`Error: ${error.response?.data?.error || error.message}`)
      } finally {
        isTestingEmail.value = false
      }
    }

    // Load config on component mount
    onMounted(fetchConfig)

    return {
      form,
      config,
      loading,
      isSaving,
      isTestingEmail,
      keywordsText,
      selectedCategories,
      categoriesDisplay,
      expandedPanels,
      enableDateRange,
      dateRange,
      yearOptions,
      monthOptions,
      emailConfig,
      fetchConfig,
      saveConfig,
      resetForm,
      isCategorySelected,
      toggleCategory,
      manualToggleCategory,
      testEmailConfig
    }
  }
}
</script>

<style scoped>
.category-select {
  transition: background-color 0.2s ease;
}

.category-select:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.category-select.selected {
  background-color: rgba(25, 118, 210, 0.1);
}
</style>