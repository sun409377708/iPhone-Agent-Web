<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-background">
    <header class="border-b">
      <div class="container mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <h1 class="text-2xl font-bold text-primary">📱 Phone-Agent-Web</h1>
          <nav class="flex gap-6">
            <router-link to="/" class="text-sm font-medium hover:text-primary transition-colors">
              首页
            </router-link>
            <router-link to="/devices" class="text-sm font-medium hover:text-primary transition-colors">
              设备管理
            </router-link>
            <router-link to="/history" class="text-sm font-medium hover:text-primary transition-colors">
              执行历史
            </router-link>
          </nav>
        </div>
      </div>
    </header>
    
    <main class="container mx-auto px-4 py-8">
      <RouterView />
    </main>
  </div>
</template>
