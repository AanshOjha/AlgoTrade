<template>
  <div class="backtest-container">
    <!-- Animated Background Elements -->
    <div class="background-animation">
      <div class="floating-shape shape-1"></div>
      <div class="floating-shape shape-2"></div>
      <div class="floating-shape shape-3"></div>
      <div class="floating-shape shape-4"></div>
      <div class="floating-shape shape-5"></div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Header Section -->
      <header class="header">
        <div class="header-content">
          <button class="back-btn" @click="goHome">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 12H5M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Back to Home
          </button>
          <h1 class="page-title">Backtest Dashboard</h1>
        </div>
      </header>

      <!-- Backtest Form Section -->
      <section class="form-section">
        <div class="form-container">
          <h2 class="section-title">Configuration</h2>
          <form @submit.prevent="runBacktest" class="backtest-form">
            <div class="form-grid">
              <!-- Stock Symbol -->
              <div class="form-group">
                <label for="stockSymbol" class="form-label">Stock Symbol</label>
                <input
                  id="stockSymbol"
                  v-model="formData.stock_symbol"
                  type="text"
                  class="form-input"
                  placeholder="e.g., AAPL"
                  required
                />
              </div>

              <!-- Strategy -->
              <div class="form-group">
                <label for="strategy" class="form-label">Strategy</label>
                <select
                  id="strategy"
                  v-model="formData.strategy_name"
                  class="form-input"
                  @change="onStrategyChange"
                  required
                >
                  <option value="ma_crossover">MA Crossover</option>
                  <option value="bollinger_bands">Bollinger Bands</option>
                </select>
              </div>

              <!-- Start Date -->
              <div class="form-group">
                <label for="startDate" class="form-label">Start Date</label>
                <input
                  id="startDate"
                  v-model="formData.start_date"
                  type="date"
                  class="form-input"
                  required
                />
              </div>

              <!-- End Date -->
              <div class="form-group">
                <label for="endDate" class="form-label">End Date</label>
                <input
                  id="endDate"
                  v-model="formData.end_date"
                  type="date"
                  class="form-input"
                  required
                />
              </div>

              <!-- Initial Capital -->
              <div class="form-group">
                <label for="initialCapital" class="form-label">Initial Capital ($)</label>
                <input
                  id="initialCapital"
                  v-model.number="formData.initial_capital"
                  type="number"
                  class="form-input"
                  placeholder="100000"
                  min="1000"
                  step="1000"
                  required
                />
              </div>

              <!-- Strategy Parameters -->
              <div class="form-group strategy-params">
                <label class="form-label">Strategy Parameters</label>
                
                <!-- MA Crossover Parameters -->
                <div v-if="formData.strategy_name === 'ma_crossover'" class="param-grid">
                  <div class="param-group">
                    <label for="shortWindow" class="param-label">Short Window</label>
                    <input
                      id="shortWindow"
                      v-model.number="formData.strategy_params.short_window"
                      type="number"
                      class="param-input"
                      min="1"
                      max="100"
                    />
                  </div>
                  <div class="param-group">
                    <label for="longWindow" class="param-label">Long Window</label>
                    <input
                      id="longWindow"
                      v-model.number="formData.strategy_params.long_window"
                      type="number"
                      class="param-input"
                      min="1"
                      max="200"
                    />
                  </div>
                </div>

                <!-- Bollinger Bands Parameters -->
                <div v-if="formData.strategy_name === 'bollinger_bands'" class="param-grid">
                  <div class="param-group">
                    <label for="window" class="param-label">Window</label>
                    <input
                      id="window"
                      v-model.number="formData.strategy_params.window"
                      type="number"
                      class="param-input"
                      min="1"
                      max="100"
                    />
                  </div>
                  <div class="param-group">
                    <label for="stdDev" class="param-label">Std Dev</label>
                    <input
                      id="stdDev"
                      v-model.number="formData.strategy_params.std_dev"
                      type="number"
                      class="param-input"
                      min="0.1"
                      max="5"
                      step="0.1"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Submit Button -->
            <div class="form-actions">
              <button
                type="submit"
                class="submit-btn"
                :disabled="isRunning"
              >
                <div class="btn-content">
                  <svg v-if="!isRunning" class="btn-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M8 5V19L19 12L8 5Z" fill="currentColor"/>
                  </svg>
                  <div v-else class="loading-spinner"></div>
                  <span>{{ isRunning ? 'Running Backtest...' : 'Run Backtest' }}</span>
                </div>
              </button>
            </div>
          </form>
        </div>
      </section>

      <!-- Status Indicator Section -->
      <section v-if="currentBacktestId" class="status-section">
        <div class="status-container">
          <div class="status-header">
            <h3 class="status-title">Backtest Status</h3>
            <div class="status-indicator" :class="statusClass">
              <div class="status-dot"></div>
              <span class="status-text">{{ statusText }}</span>
            </div>
          </div>
          
          <div v-if="isRunning" class="progress-bar">
            <div class="progress-fill"></div>
          </div>
          
          <div v-if="statusMessage" class="status-message">
            {{ statusMessage }}
          </div>
        </div>
      </section>

      <!-- Performance Summary Section -->
      <section v-if="results && !isRunning" class="results-section">
        <div class="results-container">
          <h2 class="section-title">Performance Summary</h2>
          
          <div class="metrics-grid">
            <div class="metric-card" v-for="(metric, index) in performanceMetrics" :key="index">
              <div class="metric-icon" :class="metric.type">
                <component :is="metric.icon" />
              </div>
              <div class="metric-content">
                <div class="metric-label">{{ metric.label }}</div>
                <div class="metric-value" :class="metric.valueClass">{{ metric.value }}</div>
              </div>
            </div>
          </div>

          <div class="additional-info">
            <div class="info-card">
              <h4 class="info-title">Backtest Details</h4>
              <div class="info-content">
                <div class="info-item">
                  <span class="info-label">Stock Symbol:</span>
                  <span class="info-value">{{ results.performance_report.stock_symbol }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Strategy:</span>
                  <span class="info-value">{{ formatStrategyName(results.performance_report.strategy_name) }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Backtest ID:</span>
                  <span class="info-value">{{ currentBacktestId }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Visual Analysis Section -->
      <section v-if="results && !isRunning" class="visual-section">
        <div class="visual-container">
          <h2 class="section-title">Visual Analysis</h2>
          
          <!-- Chart Tabs -->
          <div class="chart-tabs">
            <button 
              v-for="tab in chartTabs" 
              :key="tab.id"
              class="tab-button"
              :class="{ active: activeTab === tab.id }"
              @click="activeTab = tab.id"
            >
              <component :is="tab.icon" class="tab-icon" />
              <span>{{ tab.label }}</span>
            </button>
          </div>

          <!-- Chart Container -->
          <div class="chart-container">
            <!-- Price Chart Tab -->
            <div v-show="activeTab === 'price'" class="chart-tab-content">
              <div class="chart-header">
                <h3 class="chart-title">Price Chart with Signals</h3>
                <div class="chart-legend">
                  <div class="legend-item">
                    <div class="legend-color price-color"></div>
                    <span>Price</span>
                  </div>
                  <div v-if="isMAStrategy" class="legend-item">
                    <div class="legend-color ma-short-color"></div>
                    <span>Short MA</span>
                  </div>
                  <div v-if="isMAStrategy" class="legend-item">
                    <div class="legend-color ma-long-color"></div>
                    <span>Long MA</span>
                  </div>
                  <div v-if="isBBStrategy" class="legend-item">
                    <div class="legend-color bb-upper-color"></div>
                    <span>Upper Band</span>
                  </div>
                  <div v-if="isBBStrategy" class="legend-item">
                    <div class="legend-color bb-lower-color"></div>
                    <span>Lower Band</span>
                  </div>
                  <div class="legend-item">
                    <div class="legend-marker buy-marker"></div>
                    <span>Buy Signal</span>
                  </div>
                  <div class="legend-item">
                    <div class="legend-marker sell-marker"></div>
                    <span>Sell Signal</span>
                  </div>
                </div>
              </div>
              <div class="chart-wrapper">
                <canvas ref="priceChart" class="chart-canvas"></canvas>
              </div>
            </div>

            <!-- Equity Curve Tab -->
            <div v-show="activeTab === 'equity'" class="chart-tab-content">
              <div class="chart-header">
                <h3 class="chart-title">Portfolio Equity Curve</h3>
                <div class="chart-stats">
                  <div class="stat-item">
                    <span class="stat-label">Initial:</span>
                    <span class="stat-value">{{ formatCurrency(results.performance_report.initial_capital) }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">Final:</span>
                    <span class="stat-value">{{ formatCurrency(results.performance_report.final_portfolio_value) }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">Return:</span>
                    <span class="stat-value" :class="results.performance_report.total_pnl >= 0 ? 'positive' : 'negative'">
                      {{ formatPercentage(results.performance_report.total_profit_loss_pct) }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="chart-wrapper">
                <canvas ref="equityChart" class="chart-canvas"></canvas>
              </div>
            </div>

            <!-- Trade History Tab -->
            <div v-show="activeTab === 'trades'" class="chart-tab-content">
              <div class="chart-header">
                <h3 class="chart-title">Trade History</h3>
                <div class="trade-summary">
                  <div class="summary-item">
                    <span class="summary-label">Total Trades:</span>
                    <span class="summary-value">{{ results.performance_report.total_trades }}</span>
                  </div>
                  <div class="summary-item">
                    <span class="summary-label">Win Rate:</span>
                    <span class="summary-value">{{ formatPercentage(results.performance_report.win_rate_pct) }}</span>
                  </div>
                </div>
              </div>
              <div class="trades-container">
                <div class="trades-list">
                  <div v-for="(trade, index) in tradeHistory" :key="index" class="trade-item" :class="trade.pnl >= 0 ? 'profitable' : 'loss'">
                    <div class="trade-header">
                      <div class="trade-number">#{{ index + 1 }}</div>
                      <div class="trade-pnl" :class="trade.pnl >= 0 ? 'positive' : 'negative'">
                        {{ trade.pnl >= 0 ? '+' : '' }}{{ formatCurrency(trade.pnl) }}
                      </div>
                    </div>
                    <div class="trade-details">
                      <div class="trade-row">
                        <span class="trade-label">Entry:</span>
                        <span class="trade-value">{{ formatDate(trade.entryDate) }} @ {{ formatCurrency(trade.entryPrice) }}</span>
                      </div>
                      <div class="trade-row">
                        <span class="trade-label">Exit:</span>
                        <span class="trade-value">{{ formatDate(trade.exitDate) }} @ {{ formatCurrency(trade.exitPrice) }}</span>
                      </div>
                      <div class="trade-row">
                        <span class="trade-label">Duration:</span>
                        <span class="trade-value">{{ trade.duration }} days</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  TimeScale,
  PointElement,
  LineElement,
  LineController,
  ScatterController,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import 'chartjs-adapter-date-fns'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  TimeScale,
  PointElement,
  LineElement,
  LineController,
  ScatterController,
  Title,
  Tooltip,
  Legend,
  Filler,
  ScatterController
)

const router = useRouter()

// Reactive data
const formData = ref({
  stock_symbol: 'AAPL',
  start_date: '2020-01-01',
  end_date: '2024-12-31',
  initial_capital: 100000,
  strategy_name: 'ma_crossover',
  strategy_params: {
    short_window: 20,
    long_window: 50,
    window: 20,
    std_dev: 2.0
  }
})

const isRunning = ref(false)
const currentBacktestId = ref(null)
const results = ref(null)
const statusMessage = ref('')
const jobStatus = ref('PENDING')
const tradeHistoryData = ref([])
let statusCheckInterval = null

// Chart related data
const activeTab = ref('price')
const priceChart = ref(null)
const equityChart = ref(null)
let priceChartInstance = null
let equityChartInstance = null

// Simple icon components
const ChartLineIcon = {
  template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22,6 13,12 8.5,8.5 2,14"></polyline><polyline points="10,6 21,6 21,17"></polyline></svg>'
}
const TrendingUpIcon = {
  template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22,7 13.5,15.5 8.5,10.5 2,17"></polyline><polyline points="16,7 22,7 22,13"></polyline></svg>'
}
const ListIcon = {
  template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>'
}

const chartTabs = ref([
  { id: 'price', label: 'Price Chart', icon: ChartLineIcon },
  { id: 'equity', label: 'Equity Curve', icon: TrendingUpIcon },
  { id: 'trades', label: 'Trade History', icon: ListIcon }
])

// Computed properties
const statusClass = computed(() => {
  switch (jobStatus.value) {
    case 'PENDING': return 'status-pending'
    case 'RUNNING': return 'status-running'
    case 'COMPLETED': return 'status-completed'
    case 'FAILED': return 'status-failed'
    default: return 'status-pending'
  }
})

const statusText = computed(() => {
  switch (jobStatus.value) {
    case 'PENDING': return 'Pending'
    case 'RUNNING': return 'Running'
    case 'COMPLETED': return 'Completed'
    case 'FAILED': return 'Failed'
    default: return 'Unknown'
  }
})

// Performance metric icons
const PortfolioIcon = {
  template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>'
}
const PnLIcon = {
  template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>'
}
const WinRateIcon = {
  template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 12l2 2 4-4"></path><path d="M21 12c-1 0-3-1-3-3s2-3 3-3 3 1 3 3-2 3-3 3"></path><path d="M3 12c1 0 3-1 3-3s-2-3-3-3-3 1-3 3 2 3 3 3"></path></svg>'
}
const TradersIcon = {
  template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><path d="M20 8v6"></path><path d="M23 11h-6"></path></svg>'
}

const performanceMetrics = computed(() => {
  if (!results.value) return []
  
  const report = results.value.performance_report
  return [
    {
      label: 'Final Portfolio Value',
      value: formatCurrency(report.final_portfolio_value),
      type: 'primary',
      icon: PortfolioIcon,
      valueClass: 'positive'
    },
    {
      label: 'Total P&L',
      value: `${formatCurrency(report.total_pnl)} (${formatPercentage(report.total_profit_loss_pct)})`,
      type: report.total_pnl >= 0 ? 'success' : 'danger',
      icon: PnLIcon,
      valueClass: report.total_pnl >= 0 ? 'positive' : 'negative'
    },
    {
      label: 'Win Rate',
      value: formatPercentage(report.win_rate_pct),
      type: 'info',
      icon: WinRateIcon,
      valueClass: 'neutral'
    },
    {
      label: 'Total Trades',
      value: report.total_trades.toString(),
      type: 'secondary',
      icon: TradersIcon,
      valueClass: 'neutral'
    }
  ]
})

const isMAStrategy = computed(() => {
  return formData.value.strategy_name === 'ma_crossover'
})

const isBBStrategy = computed(() => {
  return formData.value.strategy_name === 'bollinger_bands'
})

const tradeHistory = computed(() => {
  // Return the fetched trade history data
  return tradeHistoryData.value.map(trade => ({
    entryDate: trade.entry_datetime,
    entryPrice: trade.entry_price,
    exitDate: trade.exit_datetime,
    exitPrice: trade.exit_price,
    pnl: trade.pnl,
    duration: trade.trade_duration_days
  }))
})

// Methods
const goHome = () => {
  router.push('/')
}

const onStrategyChange = () => {
  // Reset strategy params when strategy changes
  if (formData.value.strategy_name === 'ma_crossover') {
    formData.value.strategy_params = {
      short_window: 20,
      long_window: 50
    }
  } else if (formData.value.strategy_name === 'bollinger_bands') {
    formData.value.strategy_params = {
      window: 20,
      std_dev: 2.0
    }
  }
}

const runBacktest = async () => {
  try {
    isRunning.value = true
    results.value = null
    statusMessage.value = 'Submitting backtest request...'
    
    const response = await fetch('http://127.0.0.1:8000/backtest', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData.value)
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    
    if (data.status === 'success') {
      currentBacktestId.value = data.backtest_id
      statusMessage.value = data.message
      jobStatus.value = 'PENDING'
      
      // Start checking status
      startStatusChecking()
    } else {
      throw new Error(data.message || 'Failed to start backtest')
    }
  } catch (error) {
    console.error('Error running backtest:', error)
    statusMessage.value = `Error: ${error.message}`
    isRunning.value = false
    jobStatus.value = 'FAILED'
  }
}

const startStatusChecking = () => {
  statusCheckInterval = setInterval(async () => {
    try {
      await checkBacktestStatus()
    } catch (error) {
      console.error('Error checking status:', error)
      clearInterval(statusCheckInterval)
      isRunning.value = false
      jobStatus.value = 'FAILED'
      statusMessage.value = 'Error checking backtest status'
    }
  }, 2000) // Check every 2 seconds
}

const checkBacktestStatus = async () => {
  if (!currentBacktestId.value) return
  
  const response = await fetch(`http://127.0.0.1:8000/backtest/${currentBacktestId.value}/status`)
  const data = await response.json()
  
  if (data.job_status) {
    jobStatus.value = data.job_status
    
    if (data.job_status === 'COMPLETED') {
      clearInterval(statusCheckInterval)
      isRunning.value = false
      statusMessage.value = 'Backtest completed successfully!'
      await fetchResults()
    } else if (data.job_status === 'FAILED') {
      clearInterval(statusCheckInterval)
      isRunning.value = false
      statusMessage.value = data.error_message || 'Backtest failed'
    } else if (data.job_status === 'RUNNING') {
      statusMessage.value = 'Processing backtest data...'
    }
  }
}

const fetchTradeHistory = async () => {
  if (!currentBacktestId.value) return
  
  try {
    const response = await fetch(`http://127.0.0.1:8000/trades?backtest_id=${currentBacktestId.value}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const trades = await response.json()
    console.log('Fetched trade history:', trades) // Debug log
    
    // Filter out incomplete trades (trades without exit data)
    tradeHistoryData.value = trades.filter(trade => 
      trade.exit_datetime && trade.exit_price && trade.pnl !== null
    )
    
    console.log('Filtered trade history:', tradeHistoryData.value.length, 'completed trades')
  } catch (error) {
    console.error('Error fetching trade history:', error)
    tradeHistoryData.value = [] // Reset to empty array on error
  }
}

const fetchResults = async () => {
  if (!currentBacktestId.value) return
  
  try {
    const response = await fetch(`http://127.0.0.1:8000/backtest/${currentBacktestId.value}`)
    const data = await response.json()
    
    console.log('API Response:', data) // Debug log
    
    if (data.performance_report) {
      results.value = data
      console.log('Chart data length:', data.chart_data?.length) // Debug log
      console.log('Equity curve length:', data.equity_curve?.length) // Debug log
      
      // Fetch trade history from API
      await fetchTradeHistory()
      
      // Create charts after results are loaded
      await nextTick()
      // Wait for DOM updates and ensure canvas elements are ready
      setTimeout(() => {
        console.log('🎯 Attempting to create charts...')
        console.log('Canvas elements ready:', {
          priceChart: !!priceChart.value,
          equityChart: !!equityChart.value
        })
        createCharts()
      }, 200) // Slightly longer delay to ensure DOM is ready
    } else {
      throw new Error('No results data received')
    }
  } catch (error) {
    console.error('Error fetching results:', error)
    statusMessage.value = 'Error fetching results'
  }
}

const createCharts = () => {
  console.log('🎨 createCharts called')
  console.log('Results available:', !!results.value)
  console.log('Canvas elements:', {
    priceChart: !!priceChart.value,
    equityChart: !!equityChart.value
  })
  
  if (!results.value) {
    console.log('❌ No results available for chart creation')
    return
  }
  
  // Only create charts if canvas elements are available
  if (priceChart.value) {
    console.log('🎯 Creating price chart...')
    createPriceChart()
  } else {
    console.log('⚠️ Price chart canvas not available')
  }
  
  if (equityChart.value) {
    console.log('💰 Creating equity chart...')
    createEquityChart()
  } else {
    console.log('⚠️ Equity chart canvas not available')
  }
}

const createPriceChart = () => {
  console.log('=== CREATING PRICE CHART ===')
  console.log('priceChart.value:', priceChart.value)
  console.log('priceChart canvas element:', priceChart.value?.tagName)
  console.log('Canvas dimensions:', priceChart.value?.offsetWidth, 'x', priceChart.value?.offsetHeight)
  console.log('results.value exists:', !!results.value)
  console.log('chart_data exists:', !!results.value?.chart_data)
  console.log('chart_data length:', results.value?.chart_data?.length)
  
  if (!priceChart.value || !results.value?.chart_data || results.value.chart_data.length === 0) {
    console.log('❌ Price chart creation aborted - missing data or canvas')
    return
  }
  
  // Destroy existing chart
  if (priceChartInstance) {
    priceChartInstance.destroy()
    priceChartInstance = null
  }
  
  const chartData = results.value.chart_data
  console.log('📊 RAW CHART DATA:')
  console.log('First 3 data points:', chartData.slice(0, 3))
  console.log('Last 3 data points:', chartData.slice(-3))
  
  // Create labels and price data with proper structure for Chart.js
  const chartPoints = chartData.map(point => ({
    x: new Date(point.Date),
    y: point.Close
  }))
  
  console.log('📈 CHART POINTS FOR PRICE LINE:')
  console.log('First 3 chart points:', chartPoints.slice(0, 3))
  console.log('Last 3 chart points:', chartPoints.slice(-3))
  
  // Prepare datasets
  const datasets = [
    {
      label: 'Price',
      data: chartPoints,
      borderColor: '#3B82F6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      borderWidth: 2,
      fill: false,
      tension: 0.1,
      pointRadius: 0,
      pointHoverRadius: 4
    }
  ]
  
  // Add strategy-specific indicators
  console.log('🔧 STRATEGY DETECTION:')
  console.log('isMAStrategy:', isMAStrategy.value)
  console.log('isBBStrategy:', isBBStrategy.value)
  console.log('strategy_name:', formData.value.strategy_name)
  console.log('strategy_params:', formData.value.strategy_params)
  
  if (isMAStrategy.value) {
    const shortWindow = formData.value.strategy_params.short_window
    const longWindow = formData.value.strategy_params.long_window
    
    console.log('📊 MA STRATEGY INDICATORS:')
    console.log(`Looking for EMA${shortWindow} and EMA${longWindow} in data`)
    
    const shortMAData = chartData
      .map(point => ({ x: new Date(point.Date), y: point[`EMA${shortWindow}`] }))
      .filter(point => point.y != null)
    
    const longMAData = chartData
      .map(point => ({ x: new Date(point.Date), y: point[`EMA${longWindow}`] }))
      .filter(point => point.y != null)
    
    console.log(`EMA${shortWindow} data points:`, shortMAData.length)
    console.log(`EMA${longWindow} data points:`, longMAData.length)
    console.log(`Short MA sample:`, shortMAData.slice(0, 3))
    console.log(`Long MA sample:`, longMAData.slice(0, 3))
    
    if (shortMAData.length > 0) {
      datasets.push({
        label: `EMA${shortWindow}`,
        data: shortMAData,
        borderColor: '#10B981',
        borderWidth: 1,
        fill: false,
        pointRadius: 0
      })
    }
    
    if (longMAData.length > 0) {
      datasets.push({
        label: `EMA${longWindow}`,
        data: longMAData,
        borderColor: '#F59E0B',
        borderWidth: 1,
        fill: false,
        pointRadius: 0
      })
    }
  } else if (isBBStrategy.value) {
    console.log('📊 BOLLINGER BANDS STRATEGY INDICATORS:')
    console.log('Looking for Upper_Band, Lower_Band, SMA_20 in data')
    
    const upperBandData = chartData
      .map(point => ({ x: new Date(point.Date), y: point.Upper_Band }))
      .filter(point => point.y != null)
    
    const lowerBandData = chartData
      .map(point => ({ x: new Date(point.Date), y: point.Lower_Band }))
      .filter(point => point.y != null)
    
    const smaData = chartData
      .map(point => ({ x: new Date(point.Date), y: point[`SMA_${formData.value.strategy_params.window}`] }))
      .filter(point => point.y != null)
    
    console.log('Upper Band data points:', upperBandData.length)
    console.log('Lower Band data points:', lowerBandData.length)
    console.log('SMA data points:', smaData.length)
    console.log('Upper Band sample:', upperBandData.slice(0, 3))
    console.log('Lower Band sample:', lowerBandData.slice(0, 3))
    console.log('SMA sample:', smaData.slice(0, 3))
    
    if (upperBandData.length > 0) {
      datasets.push({
        label: 'Upper Band',
        data: upperBandData,
        borderColor: '#EF4444',
        borderWidth: 1,
        fill: false,
        pointRadius: 0
      })
    }
    
    if (lowerBandData.length > 0) {
      datasets.push({
        label: 'Lower Band',
        data: lowerBandData,
        borderColor: '#EF4444',
        borderWidth: 1,
        fill: false,
        pointRadius: 0
      })
    }
    
    if (smaData.length > 0) {
      datasets.push({
        label: 'SMA',
        data: smaData,
        borderColor: '#8B5CF6',
        borderWidth: 1,
        fill: false,
        pointRadius: 0
      })
    }
  }
  
  console.log('📍 AVAILABLE DATA KEYS IN FIRST POINT:')
  console.log('Keys:', Object.keys(chartData[0]))
  
  // Add buy/sell signals
  console.log('🎯 ANALYZING TRADING SIGNALS:')
  const positionValues = chartData.map(point => point.Position)
  console.log('All Position values:', [...new Set(positionValues)])
  console.log('Position value counts:', positionValues.reduce((acc, val) => {
    acc[val] = (acc[val] || 0) + 1
    return acc
  }, {}))
  
  const buySignals = chartData
    .map(point => point.Position === 1 ? { x: new Date(point.Date), y: point.Close } : null)
    .filter(point => point !== null)
  
  const sellSignals = chartData
    .map(point => point.Position === -1 ? { x: new Date(point.Date), y: point.Close } : null)
    .filter(point => point !== null)
  
  console.log('🟢 Buy signals found:', buySignals.length)
  console.log('Buy signals data:', buySignals)
  console.log('🔴 Sell signals found:', sellSignals.length)
  console.log('Sell signals data:', sellSignals)
  
  if (buySignals.length > 0) {
    datasets.push({
      label: 'Buy Signals',
      data: buySignals,
      backgroundColor: '#10B981',
      borderColor: '#059669',
      borderWidth: 2,
      pointRadius: 6,
      pointHoverRadius: 8,
      showLine: false,
      type: 'scatter'
    })
  }
  
  if (sellSignals.length > 0) {
    datasets.push({
      label: 'Sell Signals',
      data: sellSignals,
      backgroundColor: '#EF4444',
      borderColor: '#DC2626',
      borderWidth: 2,
      pointRadius: 6,
      pointHoverRadius: 8,
      showLine: false,
      type: 'scatter'
    })
  }
  
  console.log('📋 FINAL DATASETS FOR CHART:')
  console.log('Total datasets:', datasets.length)
  datasets.forEach((dataset, index) => {
    console.log(`Dataset ${index + 1}:`, {
      label: dataset.label,
      dataPoints: dataset.data?.length || 0,
      color: dataset.borderColor,
      sampleData: dataset.data?.slice(0, 2)
    })
  })
  
  const ctx = priceChart.value.getContext('2d')
  console.log('Canvas context:', ctx)
  
  if (!ctx) {
    console.error('❌ Failed to get 2D context from canvas element')
    return
  }
  
  console.log('🚀 Creating Chart.js instance...')
  
  try {
    priceChartInstance = new ChartJS(ctx, {
    type: 'line',
    data: {
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: false
        },
        legend: {
          display: false
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: 'white',
          bodyColor: 'white',
          borderColor: 'rgba(255, 255, 255, 0.2)',
          borderWidth: 1,
          callbacks: {
            title: function(context) {
              return new Date(context[0].parsed.x).toLocaleDateString()
            },
            label: function(context) {
              return context.dataset.label + ': $' + context.parsed.y.toFixed(2)
            }
          }
        }
      },
      scales: {
        x: {
          type: 'time',
          time: {
            unit: 'day',
            displayFormats: {
              day: 'MMM dd'
            }
          },
          grid: {
            color: 'rgba(255, 255, 255, 0.1)'
          },
          ticks: {
            color: 'rgba(255, 255, 255, 0.7)',
            maxTicksLimit: 10
          }
        },
        y: {
          grid: {
            color: 'rgba(255, 255, 255, 0.1)'
          },
          ticks: {
            color: 'rgba(255, 255, 255, 0.7)',
            callback: function(value) {
              return '$' + value.toFixed(2)
            }
          }
        }
      },
      interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
      }
    }
  })
  
    console.log('✅ Price chart created successfully!')
    console.log('Chart instance:', priceChartInstance)
  } catch (error) {
    console.error('❌ Error creating price chart:', error)
    console.error('Error stack:', error.stack)
  }
  console.log('=== END PRICE CHART CREATION ===\n')
}

const createEquityChart = () => {
  console.log('=== CREATING EQUITY CHART ===')
  console.log('equityChart.value:', equityChart.value)
  console.log('equityChart canvas element:', equityChart.value?.tagName)
  console.log('Canvas dimensions:', equityChart.value?.offsetWidth, 'x', equityChart.value?.offsetHeight)
  console.log('equity_curve exists:', !!results.value?.equity_curve)
  console.log('equity_curve length:', results.value?.equity_curve?.length)
  
  if (!equityChart.value || !results.value?.equity_curve || results.value.equity_curve.length === 0) {
    console.log('❌ Equity chart creation aborted - missing data or canvas')
    return
  }
  
  // Destroy existing chart
  if (equityChartInstance) {
    equityChartInstance.destroy()
    equityChartInstance = null
  }
  
  const equityData = results.value.equity_curve
  console.log('💰 RAW EQUITY DATA:')
  console.log('First 5 equity points:', equityData.slice(0, 5))
  console.log('Last 5 equity points:', equityData.slice(-5))
  
  // Create data points with proper structure for Chart.js
  const equityPoints = equityData.map(point => ({
    x: new Date(point.date),
    y: point.value
  }))
  
  console.log('📈 EQUITY CHART POINTS:')
  console.log('First 5 chart points:', equityPoints.slice(0, 5))
  console.log('Last 5 chart points:', equityPoints.slice(-5))
  console.log('Total equity points:', equityPoints.length)
  
  const ctx = equityChart.value.getContext('2d')
  console.log('Canvas context:', ctx)
  
  if (!ctx) {
    console.error('❌ Failed to get 2D context from equity canvas element')
    return
  }
  
  try {
    equityChartInstance = new ChartJS(ctx, {
      type: 'line',
      data: {
        datasets: [{
          label: 'Portfolio Value',
          data: equityPoints,
          borderColor: '#10B981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.2,
          pointRadius: 0,
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: 'white',
            bodyColor: 'white',
            borderColor: 'rgba(255, 255, 255, 0.2)',
            borderWidth: 1,
            callbacks: {
              title: function(context) {
                return new Date(context[0].parsed.x).toLocaleDateString()
              },
              label: function(context) {
                return 'Portfolio Value: $' + context.parsed.y.toLocaleString()
              }
            }
          }
        },
        scales: {
          x: {
            type: 'time',
            time: {
              unit: 'day',
              displayFormats: {
                day: 'MMM dd'
              }
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: 'rgba(255, 255, 255, 0.7)',
              maxTicksLimit: 10
            }
          },
          y: {
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: 'rgba(255, 255, 255, 0.7)',
              callback: function(value) {
                return '$' + value.toLocaleString()
              }
            }
          }
        }
      }
    })
    
    console.log('✅ Equity chart created successfully!')
    console.log('Chart instance:', equityChartInstance)
  } catch (error) {
    console.error('❌ Error creating equity chart:', error)
    console.error('Error stack:', error.stack)
  }
  console.log('=== END EQUITY CHART CREATION ===\n')
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

const formatPercentage = (value) => {
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
}

const formatStrategyName = (name) => {
  return name.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Watch for tab changes to resize charts and create if needed
watch(activeTab, (newTab) => {
  nextTick(() => {
    if (newTab === 'price' && !priceChartInstance && results.value) {
      createPriceChart()
    } else if (newTab === 'equity' && !equityChartInstance && results.value) {
      createEquityChart()
    }
    
    // Resize existing charts
    if (priceChartInstance) priceChartInstance.resize()
    if (equityChartInstance) equityChartInstance.resize()
  })
})

// Cleanup
onUnmounted(() => {
  if (statusCheckInterval) {
    clearInterval(statusCheckInterval)
  }
  if (priceChartInstance) {
    priceChartInstance.destroy()
  }
  if (equityChartInstance) {
    equityChartInstance.destroy()
  }
})
</script>

<style scoped>
.backtest-container {
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Background Animation (Same as Home) */
.background-animation {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
}

.floating-shape {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.shape-1 { width: 80px; height: 80px; top: 20%; left: 10%; animation-delay: 0s; }
.shape-2 { width: 120px; height: 120px; top: 60%; right: 15%; animation-delay: 2s; }
.shape-3 { width: 60px; height: 60px; bottom: 20%; left: 20%; animation-delay: 4s; }
.shape-4 { width: 100px; height: 100px; top: 10%; right: 30%; animation-delay: 1s; }
.shape-5 { width: 140px; height: 140px; bottom: 30%; right: 5%; animation-delay: 3s; }

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

/* Main Content */
.main-content {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

/* Header */
.header {
  margin-bottom: 2rem;
  animation: slideDown 0.8s ease-out;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.back-btn svg {
  width: 20px;
  height: 20px;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

/* Form Section */
.form-section {
  margin-bottom: 2rem;
  animation: fadeInUp 0.8s ease-out 0.2s both;
}

.form-container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
  margin-bottom: 1.5rem;
  text-align: center;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.strategy-params {
  grid-column: 1 / -1;
}

.form-label {
  color: white;
  font-weight: 500;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.form-input {
  padding: 0.75rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.form-input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.param-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 0.5rem;
}

.param-group {
  display: flex;
  flex-direction: column;
}

.param-label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.8rem;
  margin-bottom: 0.25rem;
}

.param-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
  font-size: 0.9rem;
}

.form-actions {
  display: flex;
  justify-content: center;
}

.submit-btn {
  padding: 1rem 3rem;
  border: none;
  border-radius: 16px;
  background: linear-gradient(135deg, #ff6b6b, #ee5a52);
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 32px rgba(255, 107, 107, 0.4);
  min-width: 200px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(255, 107, 107, 0.6);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-icon {
  width: 20px;
  height: 20px;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Status Section */
.status-section {
  margin-bottom: 2rem;
  animation: fadeInUp 0.8s ease-out 0.4s both;
}

.status-container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.status-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: white;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-pending .status-dot { background: #feca57; }
.status-running .status-dot { background: #48dbfb; }
.status-completed .status-dot { background: #1dd1a1; }
.status-failed .status-dot { background: #ff6b6b; }

.status-text {
  color: white;
  font-weight: 500;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #48dbfb, #0abde3);
  animation: loading 2s ease-in-out infinite;
}

@keyframes loading {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.status-message {
  color: rgba(255, 255, 255, 0.9);
  font-style: italic;
}

/* Results Section */
.results-section {
  margin-bottom: 2rem;
  animation: fadeInUp 0.8s ease-out 0.6s both;
}

.results-container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.metric-card:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-5px);
}

.metric-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.metric-icon.primary { background: linear-gradient(135deg, #667eea, #764ba2); }
.metric-icon.success { background: linear-gradient(135deg, #1dd1a1, #10ac84); }
.metric-icon.danger { background: linear-gradient(135deg, #ff6b6b, #ee5a52); }
.metric-icon.info { background: linear-gradient(135deg, #48dbfb, #0abde3); }
.metric-icon.secondary { background: linear-gradient(135deg, #a55eea, #8854d0); }

.metric-content {
  flex: 1;
}

.metric-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.metric-value {
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
}

.metric-value.positive { color: #1dd1a1; }
.metric-value.negative { color: #ff6b6b; }
.metric-value.neutral { color: white; }

.additional-info {
  margin-top: 2rem;
}

.info-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.info-title {
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.info-content {
  display: grid;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.info-value {
  color: white;
  font-weight: 500;
  font-family: 'Monaco', 'Menlo', monospace;
}

/* Visual Section */
.visual-section {
  animation: fadeInUp 0.8s ease-out 0.8s both;
}

.visual-container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Chart Tabs */
.chart-tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow-x: auto;
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  white-space: nowrap;
}

.tab-button:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.tab-button.active {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.tab-icon {
  width: 18px;
  height: 18px;
}

/* Chart Container */
.chart-container {
  min-height: 500px;
}

.chart-tab-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.chart-title {
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
}

.chart-legend {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.legend-color {
  width: 16px;
  height: 3px;
  border-radius: 2px;
}

.legend-marker {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.price-color { background: #3B82F6; }
.ma-short-color { background: #10B981; }
.ma-long-color { background: #F59E0B; }
.bb-upper-color { background: #EF4444; }
.bb-lower-color { background: #EF4444; }
.buy-marker { background: #10B981; }
.sell-marker { background: #EF4444; }

.chart-stats {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
}

.stat-value {
  color: white;
  font-weight: 600;
  font-size: 1rem;
}

.chart-wrapper {
  flex: 1;
  position: relative;
  min-height: 400px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  padding: 1rem;
}

.chart-canvas {
  width: 100% !important;
  height: 100% !important;
}

/* Trade History */
.trade-summary {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.summary-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.summary-value {
  color: white;
  font-weight: 600;
  font-size: 1.1rem;
}

.trades-container {
  flex: 1;
  min-height: 400px;
}

.trades-list {
  display: grid;
  gap: 1rem;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.trade-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.trade-item:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-2px);
}

.trade-item.profitable {
  border-left: 4px solid #10B981;
}

.trade-item.loss {
  border-left: 4px solid #EF4444;
}

.trade-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.trade-number {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 600;
  font-size: 0.9rem;
}

.trade-pnl {
  font-weight: 700;
  font-size: 1.1rem;
}

.trade-details {
  display: grid;
  gap: 0.5rem;
}

.trade-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.trade-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.trade-value {
  color: white;
  font-weight: 500;
  font-size: 0.9rem;
}

/* Scrollbar Styling */
.trades-list::-webkit-scrollbar {
  width: 6px;
}

.trades-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.trades-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.trades-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* Animations */
@keyframes slideDown {
  from { opacity: 0; transform: translateY(-50px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(50px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Responsive Design */
@media (max-width: 768px) {
  .main-content {
    padding: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .metric-card {
    flex-direction: column;
    text-align: center;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}

@media (max-width: 480px) {
  .form-container,
  .status-container,
  .results-container,
  .visual-container {
    padding: 1.5rem;
  }
  
  .param-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .chart-legend,
  .chart-stats,
  .trade-summary {
    flex-direction: column;
    gap: 1rem;
  }
  
  .chart-tabs {
    gap: 0.5rem;
  }
  
  .tab-button {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }
  
  .chart-wrapper {
    min-height: 300px;
  }
  
  .trade-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>