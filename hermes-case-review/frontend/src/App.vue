<template>
  <div class="h-screen flex flex-col">
    <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 shadow-sm">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-primary-500 rounded-lg flex items-center justify-center">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
        </div>
        <h1 class="text-xl font-bold text-gray-800">生态环境案卷评查系统</h1>
      </div>
      <div class="flex items-center gap-4">
        <div class="relative">
          <input 
            type="text" 
            placeholder="搜索案卷..." 
            class="w-64 pl-10 pr-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-primary-500"
          />
          <svg class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>
        <button class="relative p-2 rounded-lg hover:bg-gray-100 transition-colors">
          <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
          </svg>
          <span class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>
        <div class="flex items-center gap-2 pl-4 border-l border-gray-200">
          <div class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
            <span class="text-primary-600 font-medium">张</span>
          </div>
          <span class="text-sm text-gray-600">张三</span>
        </div>
      </div>
    </header>
    <div class="flex-1 flex overflow-hidden">
      <aside class="w-60 bg-white border-r border-gray-200 flex flex-col">
        <nav class="flex-1 py-4">
          <ul class="space-y-1 px-3">
            <li v-for="item in menuItems" :key="item.id">
              <router-link 
                :to="item.path"
                class="flex items-center gap-3 px-4 py-3 rounded-lg transition-colors"
                :class="currentPath === item.path ? 'bg-primary-50 text-primary-600 font-medium' : 'text-gray-600 hover:bg-gray-50'"
              >
                <component :is="item.icon" class="w-5 h-5" />
                <span>{{ item.name }}</span>
                <span v-if="item.badge" class="ml-auto px-2 py-0.5 text-xs rounded-full" :class="item.badgeClass">{{ item.badge }}</span>
              </router-link>
            </li>
          </ul>
        </nav>
        <div class="p-4 border-t border-gray-200">
          <div class="bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg p-4 text-white">
            <div class="text-sm opacity-80">今日评查进度</div>
            <div class="text-2xl font-bold">8/12</div>
            <div class="mt-2 h-2 bg-white/30 rounded-full overflow-hidden">
              <div class="h-full bg-white rounded-full" style="width: 67%"></div>
            </div>
          </div>
        </div>
      </aside>
      <main class="flex-1 overflow-auto bg-gray-50">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  LayoutDashboard, 
  MessageSquare, 
  Users, 
  Target, 
  BookOpen, 
  FolderOpen, 
  Settings 
} from '@element-plus/icons-vue'

const router = useRouter()
const currentPath = computed(() => router.currentRoute.value.path)

const menuItems = [
  { id: 1, name: '数据看板', path: '/dashboard', icon: LayoutDashboard },
  { id: 2, name: '审查交流', path: '/review', icon: MessageSquare, badge: '3', badgeClass: 'bg-red-500 text-white' },
  { id: 3, name: '专家团队', path: '/experts', icon: Users },
  { id: 4, name: '技能广场', path: '/skills', icon: Target },
  { id: 5, name: '知识库', path: '/knowledge', icon: BookOpen },
  { id: 6, name: '案卷管理', path: '/cases', icon: FolderOpen },
  { id: 7, name: '配置管理', path: '/settings', icon: Settings },
]
</script>
