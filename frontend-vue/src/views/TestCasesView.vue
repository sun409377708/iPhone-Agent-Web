<script setup>
import { ref, onMounted } from 'vue'
import { getTestCases, initTestCases, createTestCase, updateTestCase, deleteTestCase } from '@/api'
import { TestTube, Plus, Edit, Trash2, Play, RefreshCw, Loader2 } from 'lucide-vue-next'

const testCases = ref([])
const loading = ref(false)
const selectedCategory = ref('all')
const showCreateModal = ref(false)
const editingCase = ref(null)

const newCase = ref({
  name: '',
  description: '',
  instruction: '',
  category: 'general'
})

async function loadTestCases() {
  loading.value = true
  try {
    const category = selectedCategory.value === 'all' ? null : selectedCategory.value
    testCases.value = await getTestCases(category)
  } catch (err) {
    console.error('Failed to load test cases:', err)
  } finally {
    loading.value = false
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

async function handleCreateCase() {
  try {
    await createTestCase(newCase.value)
    showCreateModal.value = false
    resetForm()
    await loadTestCases()
  } catch (err) {
    console.error('Failed to create test case:', err)
  }
}

async function handleUpdateCase() {
  try {
    await updateTestCase(editingCase.value.id, editingCase.value)
    editingCase.value = null
    await loadTestCases()
  } catch (err) {
    console.error('Failed to update test case:', err)
  }
}

async function handleDeleteCase(id) {
  if (confirm('确定要删除这个测试用例吗？')) {
    try {
      await deleteTestCase(id)
      await loadTestCases()
    } catch (err) {
      console.error('Failed to delete test case:', err)
    }
  }
}

function startEdit(testCase) {
  editingCase.value = { ...testCase }
}

function resetForm() {
  newCase.value = {
    name: '',
    description: '',
    instruction: '',
    category: 'general'
  }
}

onMounted(() => {
  loadTestCases()
})
</script>

<template>
  <div class="h-full bg-gray-50">
    <!-- 顶部标题栏 -->
    <div class="bg-white border-b border-gray-200 px-8 py-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">测试用例管理</h1>
          <p class="text-sm text-gray-500 mt-1">创建和管理自动化测试用例</p>
        </div>
        <div class="flex gap-3">
          <button
            @click="loadTestCases"
            :disabled="loading"
            class="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
          >
            <RefreshCw :class="{ 'animate-spin': loading }" class="w-4 h-4" />
            刷新
          </button>
          <button
            v-if="testCases.length === 0"
            @click="handleInitTestCases"
            class="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            <TestTube class="w-4 h-4" />
            生成默认用例
          </button>
          <button
            @click="showCreateModal = true"
            class="flex items-center gap-2 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
          >
            <Plus class="w-4 h-4" />
            新建用例
          </button>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="p-8">
      <!-- 分类筛选 -->
      <div class="flex gap-3 mb-6">
        <button
          v-for="cat in [
            { value: 'all', label: '全部' },
            { value: 'system', label: '系统' },
            { value: 'app', label: '应用' },
            { value: 'general', label: '通用' }
          ]"
          :key="cat.value"
          @click="selectedCategory = cat.value; loadTestCases()"
          class="px-4 py-2 rounded-lg transition-colors font-medium"
          :class="selectedCategory === cat.value 
            ? 'bg-orange-500 text-white' 
            : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'"
        >
          {{ cat.label }}
        </button>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading && testCases.length === 0" class="text-center py-12">
        <Loader2 class="w-8 h-8 animate-spin mx-auto mb-2 text-orange-500" />
        <p class="text-gray-500">加载中...</p>
      </div>

      <!-- 空状态 -->
      <div v-else-if="testCases.length === 0" class="text-center py-12">
        <TestTube class="w-16 h-16 mx-auto mb-4 text-gray-300" />
        <p class="text-gray-500 mb-4">暂无测试用例</p>
        <button
          @click="handleInitTestCases"
          class="px-6 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
        >
          生成默认测试用例
        </button>
      </div>

      <!-- 测试用例列表 -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="testCase in testCases"
          :key="testCase.id"
          class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-all"
        >
          <!-- 编辑模式 -->
          <div v-if="editingCase && editingCase.id === testCase.id" class="space-y-4">
            <input
              v-model="editingCase.name"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              placeholder="用例名称"
            />
            <textarea
              v-model="editingCase.description"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              placeholder="用例描述"
              rows="2"
            />
            <textarea
              v-model="editingCase.instruction"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              placeholder="执行指令"
              rows="3"
            />
            <select
              v-model="editingCase.category"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="general">通用</option>
              <option value="system">系统</option>
              <option value="app">应用</option>
            </select>
            <div class="flex gap-2">
              <button
                @click="handleUpdateCase"
                class="flex-1 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
              >
                保存
              </button>
              <button
                @click="editingCase = null"
                class="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
              >
                取消
              </button>
            </div>
          </div>

          <!-- 显示模式 -->
          <div v-else>
            <div class="flex items-start justify-between mb-3">
              <div class="flex items-center gap-2">
                <div class="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                  <TestTube class="w-4 h-4 text-orange-600" />
                </div>
                <div>
                  <h3 class="font-semibold text-gray-800">{{ testCase.name }}</h3>
                  <span class="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded">
                    {{ testCase.category === 'system' ? '系统' : testCase.category === 'app' ? '应用' : '通用' }}
                  </span>
                </div>
              </div>
            </div>
            
            <p class="text-sm text-gray-600 mb-3">{{ testCase.description }}</p>
            
            <div class="bg-gray-50 rounded-lg p-3 mb-4">
              <p class="text-xs text-gray-500 mb-1">执行指令:</p>
              <p class="text-sm text-gray-700">{{ testCase.instruction }}</p>
            </div>

            <div class="flex gap-2">
              <button
                @click="startEdit(testCase)"
                class="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
              >
                <Edit class="w-4 h-4" />
                编辑
              </button>
              <button
                @click="handleDeleteCase(testCase.id)"
                class="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors"
              >
                <Trash2 class="w-4 h-4" />
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建用例弹窗 -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showCreateModal = false"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">创建测试用例</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-2">用例名称</label>
            <input
              v-model="newCase.name"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              placeholder="例如: 打开微信"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2">用例描述</label>
            <textarea
              v-model="newCase.description"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              placeholder="描述这个测试用例的功能"
              rows="2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2">执行指令</label>
            <textarea
              v-model="newCase.instruction"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              placeholder="输入要执行的自然语言指令"
              rows="3"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2">分类</label>
            <select
              v-model="newCase.category"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="general">通用</option>
              <option value="system">系统</option>
              <option value="app">应用</option>
            </select>
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button
            @click="handleCreateCase"
            :disabled="!newCase.name || !newCase.instruction"
            class="flex-1 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            创建
          </button>
          <button
            @click="showCreateModal = false; resetForm()"
            class="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            取消
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
