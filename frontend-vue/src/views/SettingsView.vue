<script setup>
import { ref, onMounted } from 'vue'
import { Settings, Save, Key, Cpu, Globe, RefreshCw } from 'lucide-vue-next'

const config = ref({
  apiKey: '',
  modelType: 'glm-4',
  baseUrl: 'https://open.bigmodel.cn/api/paas/v4',
  temperature: 0.7,
  maxTokens: 2000
})

const saved = ref(false)
const loading = ref(false)

async function loadConfig() {
  loading.value = true
  try {
    const response = await fetch('http://localhost:5001/api/config')
    if (response.ok) {
      const data = await response.json()
      if (data.config) {
        config.value = { ...config.value, ...data.config }
      }
    }
  } catch (err) {
    console.error('Failed to load config:', err)
  } finally {
    loading.value = false
  }
}

async function saveConfig() {
  loading.value = true
  saved.value = false
  try {
    const response = await fetch('http://localhost:5001/api/config', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config.value),
    })
    
    if (response.ok) {
      saved.value = true
      setTimeout(() => {
        saved.value = false
      }, 3000)
    }
  } catch (err) {
    console.error('Failed to save config:', err)
    alert('保存失败，请检查后端服务是否正常运行')
  } finally {
    loading.value = false
  }
}

function resetToDefault() {
  if (confirm('确定要重置为默认配置吗？')) {
    config.value = {
      apiKey: '',
      modelType: 'glm-4',
      baseUrl: 'https://open.bigmodel.cn/api/paas/v4',
      temperature: 0.7,
      maxTokens: 2000
    }
  }
}

onMounted(() => {
  loadConfig()
})
</script>

<template>
  <div class="h-full bg-gray-50">
    <!-- 顶部标题栏 -->
    <div class="bg-white border-b border-gray-200 px-8 py-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">系统设置</h1>
          <p class="text-sm text-gray-500 mt-1">配置 AI 模型和系统参数</p>
        </div>
        <div class="flex gap-3">
          <button
            @click="resetToDefault"
            class="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <RefreshCw class="w-4 h-4" />
            重置默认
          </button>
          <button
            @click="saveConfig"
            :disabled="loading"
            class="flex items-center gap-2 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:opacity-50 transition-colors"
          >
            <Save class="w-4 h-4" />
            {{ loading ? '保存中...' : '保存配置' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="p-8 max-w-4xl">
      <!-- 成功提示 -->
      <div
        v-if="saved"
        class="mb-6 bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3"
      >
        <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div>
          <p class="font-medium text-green-800">配置已保存</p>
          <p class="text-sm text-green-600">新配置将在下次执行任务时生效</p>
        </div>
      </div>

      <!-- AI 模型配置 -->
      <div class="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
            <Cpu class="w-5 h-5 text-orange-600" />
          </div>
          <div>
            <h2 class="text-lg font-semibold text-gray-800">AI 模型配置</h2>
            <p class="text-sm text-gray-500">配置智谱 AI GLM 模型参数</p>
          </div>
        </div>

        <div class="space-y-5">
          <!-- API Key -->
          <div>
            <label class="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Key class="w-4 h-4" />
              API Key
              <span class="text-red-500">*</span>
            </label>
            <input
              v-model="config.apiKey"
              type="password"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="请输入智谱 AI 的 API Key"
            />
            <p class="text-xs text-gray-500 mt-2">
              在 <a href="https://open.bigmodel.cn" target="_blank" class="text-orange-500 hover:underline">智谱 AI 开放平台</a> 获取 API Key
            </p>
          </div>

          <!-- 模型类型 -->
          <div>
            <label class="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Cpu class="w-4 h-4" />
              模型类型
            </label>
            <select
              v-model="config.modelType"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            >
              <option value="glm-4">GLM-4 (推荐)</option>
              <option value="glm-4-plus">GLM-4-Plus (更强大)</option>
              <option value="glm-4-air">GLM-4-Air (更快速)</option>
              <option value="glm-4-flash">GLM-4-Flash (极速)</option>
            </select>
            <p class="text-xs text-gray-500 mt-2">
              不同模型在性能和成本上有所差异，GLM-4 适合大多数场景
            </p>
          </div>

          <!-- Base URL -->
          <div>
            <label class="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Globe class="w-4 h-4" />
              API Base URL
            </label>
            <input
              v-model="config.baseUrl"
              type="text"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              placeholder="https://open.bigmodel.cn/api/paas/v4"
            />
            <p class="text-xs text-gray-500 mt-2">
              通常无需修改，除非使用自定义代理或企业版
            </p>
          </div>
        </div>
      </div>

      <!-- 高级参数 -->
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <Settings class="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h2 class="text-lg font-semibold text-gray-800">高级参数</h2>
            <p class="text-sm text-gray-500">调整模型生成参数</p>
          </div>
        </div>

        <div class="space-y-5">
          <!-- Temperature -->
          <div>
            <label class="text-sm font-medium text-gray-700 mb-2 flex items-center justify-between">
              <span>Temperature (温度)</span>
              <span class="text-orange-600 font-mono">{{ config.temperature }}</span>
            </label>
            <input
              v-model.number="config.temperature"
              type="range"
              min="0"
              max="1"
              step="0.1"
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-orange-500"
            />
            <div class="flex justify-between text-xs text-gray-500 mt-2">
              <span>更保守 (0.0)</span>
              <span>更随机 (1.0)</span>
            </div>
            <p class="text-xs text-gray-500 mt-2">
              控制输出的随机性，较低的值使输出更确定，较高的值使输出更多样
            </p>
          </div>

          <!-- Max Tokens -->
          <div>
            <label class="text-sm font-medium text-gray-700 mb-2 flex items-center justify-between">
              <span>Max Tokens (最大令牌数)</span>
              <span class="text-orange-600 font-mono">{{ config.maxTokens }}</span>
            </label>
            <input
              v-model.number="config.maxTokens"
              type="range"
              min="500"
              max="4000"
              step="100"
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-orange-500"
            />
            <div class="flex justify-between text-xs text-gray-500 mt-2">
              <span>500</span>
              <span>4000</span>
            </div>
            <p class="text-xs text-gray-500 mt-2">
              限制模型生成的最大长度，较大的值允许更长的输出但消耗更多资源
            </p>
          </div>
        </div>
      </div>

      <!-- 提示信息 -->
      <div class="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex gap-3">
          <div class="flex-shrink-0">
            <svg class="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="text-sm text-blue-800">
            <p class="font-medium mb-1">配置说明</p>
            <ul class="list-disc list-inside space-y-1 text-blue-700">
              <li>API Key 是必填项，请确保填写正确的密钥</li>
              <li>修改配置后需要点击"保存配置"按钮才能生效</li>
              <li>配置保存在后端，重启服务后仍然有效</li>
              <li>如遇到问题，可以点击"重置默认"恢复初始配置</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
