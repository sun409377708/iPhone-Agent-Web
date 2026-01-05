<script setup>
import { ref, onMounted } from 'vue'
import { fetchHistory } from '@/api'
import { Clock, CheckCircle, XCircle, Loader2, RefreshCw } from 'lucide-vue-next'

const history = ref([])
const loading = ref(false)

async function loadHistory() {
  loading.value = true
  try {
    const data = await fetchHistory()
    history.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('Failed to load history:', error)
    history.value = []
  } finally {
    loading.value = false
  }
}

function getStatusIcon(status) {
  switch (status) {
    case 'completed':
      return CheckCircle
    case 'failed':
      return XCircle
    case 'running':
      return Loader2
    default:
      return Clock
  }
}

function getStatusColor(status) {
  switch (status) {
    case 'completed':
      return 'text-green-600 bg-green-50'
    case 'failed':
      return 'text-red-600 bg-red-50'
    case 'running':
      return 'text-blue-600 bg-blue-50'
    default:
      return 'text-gray-600 bg-gray-50'
  }
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadHistory()
})
</script>

<template>
  <div class="h-full bg-gray-50">
    <!-- 顶部标题栏 -->
    <div class="bg-white border-b border-gray-200 px-8 py-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">执行历史</h1>
          <p class="text-sm text-gray-500 mt-1">查看所有任务的执行历史和结果详情</p>
        </div>
        <button
          @click="loadHistory"
          :disabled="loading"
          class="flex items-center gap-2 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:opacity-50 transition-colors"
        >
          <RefreshCw :class="{ 'animate-spin': loading }" class="w-4 h-4" />
          刷新
        </button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="p-8 space-y-6">

    <div v-if="loading && history.length === 0" class="text-center py-12">
      <Loader2 class="w-8 h-8 animate-spin mx-auto mb-2 text-primary" />
      <p class="text-muted-foreground">加载中...</p>
    </div>

    <div v-else-if="history.length === 0" class="text-center py-12">
      <Clock class="w-12 h-12 mx-auto mb-4 text-gray-400" />
      <p class="text-muted-foreground">暂无执行记录</p>
      <p class="text-sm text-muted-foreground mt-2">执行任务后将在此显示历史记录</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="item in history"
        :key="item.id"
        class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <component
                :is="getStatusIcon(item.status)"
                :class="[
                  'w-5 h-5',
                  item.status === 'running' ? 'animate-spin' : ''
                ]"
              />
              <h3 class="font-semibold text-lg">{{ item.task_description }}</h3>
            </div>
            <p class="text-sm text-muted-foreground">
              创建时间: {{ formatDate(item.created_at) }}
            </p>
            <p v-if="item.finished_at" class="text-sm text-muted-foreground">
              完成时间: {{ formatDate(item.finished_at) }}
            </p>
          </div>
          <span
            :class="[
              'px-3 py-1 text-sm font-medium rounded-full',
              getStatusColor(item.status)
            ]"
          >
            {{ item.status === 'completed' ? '已完成' : 
               item.status === 'failed' ? '失败' : 
               item.status === 'running' ? '运行中' : '未知' }}
          </span>
        </div>

        <div v-if="item.result_message" class="mt-4 p-4 bg-gray-50 rounded-lg">
          <p class="text-sm font-medium mb-2">执行结果:</p>
          <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ item.result_message }}</p>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>
