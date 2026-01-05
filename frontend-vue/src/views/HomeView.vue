<script setup>
import { useRouter } from 'vue-router'
import { Smartphone, History, Play } from 'lucide-vue-next'

const router = useRouter()

function navigateTo(path) {
  router.push(path)
}
</script>

<template>
  <div class="space-y-8">
    <div class="text-center py-12">
      <h1 class="text-4xl font-bold mb-4">欢迎使用 Phone-Agent-Web</h1>
      <p class="text-muted-foreground text-lg">
        iOS/Android 自动化测试平台
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <button
        @click="navigateTo('/devices')"
        class="p-6 bg-white border-2 border-gray-200 rounded-lg hover:border-primary hover:shadow-lg transition-all text-left group"
      >
        <div class="flex items-center justify-center w-12 h-12 bg-primary/10 rounded-full mb-4 group-hover:bg-primary/20 transition-colors">
          <Smartphone class="w-6 h-6 text-primary" />
        </div>
        <h3 class="text-xl font-semibold mb-2 group-hover:text-primary transition-colors">设备管理</h3>
        <p class="text-muted-foreground text-sm">
          查看和管理已连接的 iOS/Android 设备，执行自动化任务
        </p>
      </button>

      <button
        @click="navigateTo('/history')"
        class="p-6 bg-white border-2 border-gray-200 rounded-lg hover:border-primary hover:shadow-lg transition-all text-left group"
      >
        <div class="flex items-center justify-center w-12 h-12 bg-primary/10 rounded-full mb-4 group-hover:bg-primary/20 transition-colors">
          <History class="w-6 h-6 text-primary" />
        </div>
        <h3 class="text-xl font-semibold mb-2 group-hover:text-primary transition-colors">执行历史</h3>
        <p class="text-muted-foreground text-sm">
          查看所有任务的执行历史和结果详情
        </p>
      </button>

      <button
        @click="navigateTo('/devices')"
        class="p-6 bg-white border-2 border-gray-200 rounded-lg hover:border-primary hover:shadow-lg transition-all text-left group"
      >
        <div class="flex items-center justify-center w-12 h-12 bg-primary/10 rounded-full mb-4 group-hover:bg-primary/20 transition-colors">
          <Play class="w-6 h-6 text-primary" />
        </div>
        <h3 class="text-xl font-semibold mb-2 group-hover:text-primary transition-colors">测试用例</h3>
        <p class="text-muted-foreground text-sm">
          快速选择预设测试用例，一键执行自动化任务
        </p>
      </button>
    </div>

    <div class="bg-gradient-to-r from-primary/10 to-primary/5 border border-primary/20 rounded-lg p-6">
      <h2 class="text-xl font-semibold mb-4">🚀 快速开始</h2>
      <ol class="space-y-3 text-sm">
        <li class="flex items-start gap-3">
          <span class="flex-shrink-0 w-6 h-6 bg-primary text-white rounded-full flex items-center justify-center text-xs font-bold">1</span>
          <span>通过 USB 连接 iOS 设备，确保 WebDriverAgent 已安装并运行</span>
        </li>
        <li class="flex items-start gap-3">
          <span class="flex-shrink-0 w-6 h-6 bg-primary text-white rounded-full flex items-center justify-center text-xs font-bold">2</span>
          <span>前往"设备管理"页面，确认设备已成功连接</span>
        </li>
        <li class="flex items-start gap-3">
          <span class="flex-shrink-0 w-6 h-6 bg-primary text-white rounded-full flex items-center justify-center text-xs font-bold">3</span>
          <span>在任务输入框中输入自然语言指令，例如："打开微信，发送消息给张三"</span>
        </li>
        <li class="flex items-start gap-3">
          <span class="flex-shrink-0 w-6 h-6 bg-primary text-white rounded-full flex items-center justify-center text-xs font-bold">4</span>
          <span>点击"执行任务"按钮，实时查看执行日志和结果</span>
        </li>
      </ol>
    </div>
  </div>
</template>
