<script setup>
import { RouterView } from 'vue-router'
import { Smartphone, TestTube, History, Settings } from 'lucide-vue-next'
</script>

<template>
  <div class="flex h-screen bg-gray-50">
    <!-- 左侧导航栏 -->
    <aside class="w-64 bg-white border-r border-gray-200 flex flex-col">
      <!-- Logo 区域 -->
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-gradient-to-br from-orange-400 to-orange-600 rounded-lg flex items-center justify-center">
            <Smartphone class="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 class="text-lg font-bold text-gray-800">Phone<span class="text-orange-500">Agent</span>Web</h1>
            <p class="text-xs text-gray-500">iOS 自动化测试平台</p>
          </div>
        </div>
      </div>

      <!-- 导航菜单 -->
      <nav class="flex-1 p-4 space-y-2">
        <router-link
          to="/devices"
          class="flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group"
          active-class="bg-orange-50 text-orange-600"
          exact-active-class="bg-orange-50 text-orange-600"
        >
          <Smartphone class="w-5 h-5 group-[.router-link-active]:text-orange-600 text-gray-500" />
          <span class="font-medium">设备管理</span>
        </router-link>

        <router-link
          to="/test-cases"
          class="flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group"
          active-class="bg-orange-50 text-orange-600"
        >
          <TestTube class="w-5 h-5 group-[.router-link-active]:text-orange-600 text-gray-500" />
          <span class="font-medium">测试用例</span>
        </router-link>

        <router-link
          to="/history"
          class="flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group"
          active-class="bg-orange-50 text-orange-600"
        >
          <History class="w-5 h-5 group-[.router-link-active]:text-orange-600 text-gray-500" />
          <span class="font-medium">执行历史</span>
        </router-link>

        <router-link
          to="/settings"
          class="flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group"
          active-class="bg-orange-50 text-orange-600"
        >
          <Settings class="w-5 h-5 group-[.router-link-active]:text-orange-600 text-gray-500" />
          <span class="font-medium">设置</span>
        </router-link>
      </nav>

      <!-- 底部版本信息 -->
      <div class="p-4 border-t border-gray-200">
        <p class="text-xs text-gray-400 text-center">v1.0.0</p>
      </div>
    </aside>

    <!-- 右侧主内容区 -->
    <main class="flex-1 overflow-auto">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.router-link-active {
  @apply bg-orange-50 text-orange-600;
}

.router-link-active .lucide {
  @apply text-orange-600;
}
</style>
