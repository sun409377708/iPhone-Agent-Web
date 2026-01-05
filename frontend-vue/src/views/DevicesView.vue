<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { fetchDevices, runTask, createLogStream, getScreenshot, getTestCases, initTestCases } from '@/api'
import { Smartphone, RefreshCw, Play, Loader2, Monitor, TestTube, Plus } from 'lucide-vue-next'

const devices = ref([])
const loading = ref(false)
const instruction = ref('')
const logs = ref([])
const isRunning = ref(false)
const error = ref(null)
const screenshot = ref(null)
const showScreenshot = ref(false)
const screenshotLoading = ref(false)
const testCases = ref([])
const selectedCategory = ref('all')
const showTestCases = ref(true)
let logStream = null
let screenshotInterval = null

async function loadDevices() {
  loading.value = true
  error.value = null
  try {
    const data = await fetchDevices()
    devices.value = data.devices || []
  } catch (err) {
    console.error('Failed to load devices:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function setupLogStream() {
  if (logStream) {
    logStream.close()
  }

  logStream = createLogStream(
    (message) => {
      // message 现在是纯文本字符串
      if (message === 'END') {
        isRunning.value = false
        logs.value.push({
          timestamp: new Date().toLocaleTimeString(),
          message: '✅ 任务执行结束'
        })
      } else if (message && message.trim()) {
        logs.value.push({
          timestamp: new Date().toLocaleTimeString(),
          message: message
        })
      }
      // 自动滚动到底部
      setTimeout(() => {
        const logContainer = document.querySelector('.max-h-96')
        if (logContainer) {
          logContainer.scrollTop = logContainer.scrollHeight
        }
      }, 100)
    },
    (error) => {
      console.error('Log stream error:', error)
      isRunning.value = false
    }
  )
}

async function handleRunTask() {
  if (!instruction.value.trim()) {
    alert('请输入任务指令')
    return
  }

  isRunning.value = true
  logs.value = []
  
  // 先建立日志流连接
  setupLogStream()
  
  // 等待一下确保连接建立
  await new Promise(resolve => setTimeout(resolve, 500))

  try {
    const result = await runTask(instruction.value)
    console.log('Task started:', result)
  } catch (error) {
    console.error('Failed to run task:', error)
    alert('任务执行失败: ' + error.message)
    isRunning.value = false
  }
}

function stopTask() {
  if (logStream) {
    logStream.close()
    logStream = null
  }
  isRunning.value = false
}

function getLogColor(message) {
  if (message.includes('✅') || message.includes('完成')) {
    return 'text-green-400'
  } else if (message.includes('❌') || message.includes('错误') || message.includes('失败')) {
    return 'text-red-400'
  } else if (message.includes('🤖') || message.includes('AI') || message.includes('思考')) {
    return 'text-blue-400'
  } else if (message.includes('📝') || message.includes('开始')) {
    return 'text-yellow-400'
  } else if (message.includes('💭') || message.includes('分析')) {
    return 'text-purple-400'
  } else if (message.includes('🎯') || message.includes('执行')) {
    return 'text-cyan-400'
  }
  return 'text-green-400'
}

async function loadScreenshot() {
  try {
    screenshotLoading.value = true
    const data = await getScreenshot()
    if (data.success) {
      screenshot.value = data.image
    }
  } catch (err) {
    console.error('Failed to load screenshot:', err)
  } finally {
    screenshotLoading.value = false
  }
}

function toggleScreenshot() {
  showScreenshot.value = !showScreenshot.value
  if (showScreenshot.value) {
    // 立即加载一次截图
    loadScreenshot()
    // 每2秒自动刷新截图
    screenshotInterval = setInterval(loadScreenshot, 2000)
  } else {
    // 停止自动刷新
    if (screenshotInterval) {
      clearInterval(screenshotInterval)
      screenshotInterval = null
    }
  }
}

async function loadTestCases() {
  try {
    const category = selectedCategory.value === 'all' ? null : selectedCategory.value
    testCases.value = await getTestCases(category)
  } catch (err) {
    console.error('Failed to load test cases:', err)
  }
}

async function handleInitTestCases() {
  try {
    await initTestCases()
    await loadTestCases()
  } catch (err) {
    console.error('Failed to initialize test cases:', err)
  }
}

function selectTestCase(testCase) {
  instruction.value = testCase.instruction
}

onMounted(() => {
  loadDevices()
  loadTestCases()
})

onUnmounted(() => {
  // 清理定时器
  if (screenshotInterval) {
    clearInterval(screenshotInterval)
  }
  // 清理日志流
  if (logStream) {
    logStream.close()
  }
})
</script>

<template>
  <div class="h-full bg-gray-50">
    <!-- 顶部标题栏 -->
    <div class="bg-white border-b border-gray-200 px-8 py-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">设备管理</h1>
          <p class="text-sm text-gray-500 mt-1">管理已连接的 iOS/Android 设备</p>
        </div>
        <button
          @click="loadDevices"
          :disabled="loading"
          class="flex items-center gap-2 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:opacity-50 transition-colors"
        >
          <RefreshCw :class="{ 'animate-spin': loading }" class="w-4 h-4" />
          刷新设备
        </button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="p-8 space-y-6">

    <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
      <p class="text-red-700 text-sm">⚠️ {{ error }}</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-if="loading && devices.length === 0"
        class="col-span-full text-center py-12 text-muted-foreground"
      >
        <Loader2 class="w-8 h-8 animate-spin mx-auto mb-2" />
        加载中...
      </div>

      <div
        v-else-if="devices.length === 0 && !error"
        class="col-span-full text-center py-12 text-muted-foreground"
      >
        <Smartphone class="w-12 h-12 mx-auto mb-4 opacity-50" />
        <p>暂无设备连接</p>
        <p class="text-sm mt-2">请通过 USB 连接 iOS 或 Android 设备</p>
      </div>

      <div
        v-for="device in devices"
        :key="device.id"
        class="p-6 bg-white border border-gray-200 rounded-lg hover:shadow-lg transition-shadow"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
              <Smartphone class="w-5 h-5 text-primary" />
            </div>
            <div>
              <h3 class="font-semibold">{{ device.name || '未命名设备' }}</h3>
              <p class="text-sm text-muted-foreground">{{ device.platform || 'iOS' }}</p>
            </div>
          </div>
          <span class="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded-full">
            在线
          </span>
        </div>

        <div class="space-y-2 text-sm text-muted-foreground">
          <div class="flex justify-between">
            <span>设备 ID:</span>
            <span class="font-mono text-xs">{{ device.id || 'N/A' }}</span>
          </div>
          <div class="flex justify-between">
            <span>型号:</span>
            <span>{{ device.model || 'Unknown' }}</span>
          </div>
          <div class="flex justify-between">
            <span>系统版本:</span>
            <span>{{ device.version || 'N/A' }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="border-t pt-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-2xl font-bold">🎯 执行任务</h2>
        <button
          v-if="testCases.length === 0"
          @click="handleInitTestCases"
          class="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm"
        >
          <Plus class="w-4 h-4" />
          生成测试用例
        </button>
      </div>

      <!-- 测试用例快速选择 -->
      <div v-if="testCases.length > 0" class="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold flex items-center gap-2">
            <TestTube class="w-5 h-5 text-blue-600" />
            快速测试用例
          </h3>
          <div class="flex gap-2">
            <button
              v-for="cat in ['all', 'system', 'app']"
              :key="cat"
              @click="selectedCategory = cat; loadTestCases()"
              class="px-3 py-1 text-sm rounded-lg transition-colors"
              :class="selectedCategory === cat ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'"
            >
              {{ cat === 'all' ? '全部' : cat === 'system' ? '系统' : '应用' }}
            </button>
          </div>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2">
          <button
            v-for="testCase in testCases"
            :key="testCase.id"
            @click="selectTestCase(testCase)"
            :disabled="isRunning"
            class="px-3 py-2 bg-white border border-blue-300 rounded-lg hover:bg-blue-50 hover:border-blue-500 transition-colors text-sm text-left disabled:opacity-50 disabled:cursor-not-allowed"
            :title="testCase.description"
          >
            <div class="font-medium text-gray-900">{{ testCase.name }}</div>
            <div class="text-xs text-gray-500 truncate">{{ testCase.description }}</div>
          </button>
        </div>
      </div>
      
      <!-- 左右布局：左边命令，右边投屏 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 左侧：任务执行区域 -->
        <div class="bg-white border border-gray-200 rounded-lg p-6">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-2">任务指令</label>
              <textarea
                v-model="instruction"
                :disabled="isRunning"
                placeholder="例如：打开微信，点击通讯录"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
              ></textarea>
            </div>

            <div class="flex gap-2">
              <button
                v-if="!isRunning"
                @click="handleRunTask"
                :disabled="!instruction.trim()"
                class="flex items-center gap-2 px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-colors"
              >
                <Play class="w-4 h-4" />
                执行任务
              </button>
              <button
                v-else
                @click="stopTask"
                class="flex items-center gap-2 px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
              >
                停止
              </button>
            </div>
          </div>

          <div v-if="logs.length > 0" class="mt-6">
            <h3 class="text-sm font-medium mb-2 flex items-center gap-2">
              <span>执行日志</span>
              <span v-if="isRunning" class="text-xs text-primary">运行中...</span>
            </h3>
            <div class="bg-gray-900 text-green-400 rounded-lg p-4 max-h-96 overflow-y-auto font-mono text-sm">
              <div v-for="(log, index) in logs" :key="index" class="mb-1 leading-relaxed">
                <span class="text-gray-500">[{{ log.timestamp }}]</span> 
                <span :class="getLogColor(log.message)">{{ log.message }}</span>
              </div>
              <div v-if="isRunning" class="mt-2 text-yellow-400 animate-pulse">
                ⏳ 正在执行中...
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：屏幕投屏区域 -->
        <div class="bg-white border border-gray-200 rounded-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-bold flex items-center gap-2">
              <Monitor class="w-5 h-5 text-primary" />
              实时屏幕投屏
            </h3>
            <button
              @click="toggleScreenshot"
              class="px-3 py-1 text-sm rounded-lg transition-colors"
              :class="showScreenshot ? 'bg-red-100 text-red-700 hover:bg-red-200' : 'bg-primary/10 text-primary hover:bg-primary/20'"
            >
              {{ showScreenshot ? '停止' : '开始' }}
            </button>
          </div>

          <div class="flex justify-center items-center min-h-[400px]">
            <div v-if="showScreenshot">
              <div v-if="screenshot" class="relative">
                <img 
                  :src="screenshot" 
                  alt="设备屏幕" 
                  class="w-full h-auto border border-gray-300 rounded-lg shadow-lg"
                />
                <div class="mt-2 text-center text-xs text-muted-foreground">
                  每 2 秒自动刷新
                </div>
              </div>
              <div v-else class="text-center text-muted-foreground">
                <Loader2 class="w-8 h-8 animate-spin mx-auto mb-2" />
                <p>正在加载屏幕截图...</p>
              </div>
            </div>
            <div v-else class="text-center text-muted-foreground">
              <Monitor class="w-16 h-16 mx-auto mb-4 opacity-30" />
              <p>点击"开始"按钮查看实时屏幕</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>
