<template>
  <div class="p-6">
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-gray-800">数据看板</h2>
      <p class="text-gray-500 mt-1">实时监控系统运行状态和评查数据</p>
    </div>
    
    <div class="grid grid-cols-4 gap-4 mb-6">
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-sm text-gray-500">累计评查</div>
            <div class="text-3xl font-bold text-gray-800 mt-2">1,234</div>
            <div class="text-sm text-green-500 mt-1">+12.5%</div>
          </div>
          <div class="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-sm text-gray-500">本月新增</div>
            <div class="text-3xl font-bold text-gray-800 mt-2">156</div>
            <div class="text-sm text-green-500 mt-1">+23.1%</div>
          </div>
          <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-sm text-gray-500">平均耗时</div>
            <div class="text-3xl font-bold text-gray-800 mt-2">3分42秒</div>
            <div class="text-sm text-green-500 mt-1">-15.2%</div>
          </div>
          <div class="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-sm text-gray-500">好评率</div>
            <div class="text-3xl font-bold text-gray-800 mt-2">96.8%</div>
            <div class="text-sm text-green-500 mt-1">+2.3%</div>
          </div>
          <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path>
            </svg>
          </div>
        </div>
      </div>
    </div>
    
    <div class="grid grid-cols-3 gap-6">
      <div class="col-span-2 bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-gray-800">评查趋势</h3>
          <div class="flex gap-2">
            <button class="px-3 py-1 text-sm rounded-lg bg-primary-500 text-white">本周</button>
            <button class="px-3 py-1 text-sm rounded-lg text-gray-600 hover:bg-gray-100">本月</button>
            <button class="px-3 py-1 text-sm rounded-lg text-gray-600 hover:bg-gray-100">全年</button>
          </div>
        </div>
        <div class="h-64 flex items-end gap-4">
          <div v-for="(value, index) in chartData" :key="index" class="flex-1 flex flex-col items-center gap-2">
            <div class="w-full bg-primary-500 rounded-t-lg transition-all" :style="{ height: `${value}%` }"></div>
            <span class="text-xs text-gray-500">{{ ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][index] }}</span>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 class="text-lg font-semibold text-gray-800 mb-6">智能体表现排行</h3>
        <div class="space-y-4">
          <div v-for="(agent, index) in agentRanking" :key="agent.id" class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold" :class="index < 3 ? 'bg-primary-500 text-white' : 'bg-gray-100 text-gray-600'">
              {{ index + 1 }}
            </div>
            <div class="flex-1">
              <div class="flex items-center justify-between">
                <span class="font-medium text-gray-800">{{ agent.name }}</span>
                <span class="text-sm text-gray-500">{{ agent.successRate }}%</span>
              </div>
              <div class="h-2 bg-gray-100 rounded-full mt-1 overflow-hidden">
                <div class="h-full bg-primary-500 rounded-full" :style="{ width: `${agent.successRate}%` }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="grid grid-cols-2 gap-6 mt-6">
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 class="text-lg font-semibold text-gray-800 mb-6">评分分布</h3>
        <div class="flex items-center justify-center">
          <div class="relative w-48 h-48">
            <svg viewBox="0 0 100 100" class="w-full h-full transform -rotate-90">
              <circle cx="50" cy="50" r="40" fill="none" stroke="#f3f4f6" stroke-width="12"/>
              <circle cx="50" cy="50" r="40" fill="none" stroke="#1a75ff" stroke-width="12" stroke-dasharray="251" stroke-dashoffset="0"/>
              <circle cx="50" cy="50" r="40" fill="none" stroke="#52c41a" stroke-width="12" stroke-dasharray="251" stroke-dashoffset="-62.75"/>
              <circle cx="50" cy="50" r="40" fill="none" stroke="#faad14" stroke-width="12" stroke-dasharray="251" stroke-dashoffset="-125.5"/>
              <circle cx="50" cy="50" r="40" fill="none" stroke="#f5222d" stroke-width="12" stroke-dasharray="251" stroke-dashoffset="-188.25"/>
            </svg>
            <div class="absolute inset-0 flex items-center justify-center">
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-800">1234</div>
                <div class="text-xs text-gray-500">总案件</div>
              </div>
            </div>
          </div>
          <div class="ml-8 space-y-3">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-primary-500"></div>
              <span class="text-sm text-gray-600">优秀 (35%)</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-green-500"></div>
              <span class="text-sm text-gray-600">良好 (30%)</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
              <span class="text-sm text-gray-600">合格 (25%)</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-red-500"></div>
              <span class="text-sm text-gray-600">不合格 (10%)</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 class="text-lg font-semibold text-gray-800 mb-6">最近评查</h3>
        <div class="space-y-4">
          <div v-for="caseItem in recentCases" :key="caseItem.id" class="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
              </div>
              <div>
                <div class="font-medium text-gray-800">{{ caseItem.name }}</div>
                <div class="text-sm text-gray-500">{{ caseItem.time }}</div>
              </div>
            </div>
            <div class="text-right">
              <div class="font-bold" :class="caseItem.score >= 80 ? 'text-green-500' : caseItem.score >= 60 ? 'text-yellow-500' : 'text-red-500'">{{ caseItem.score }}</div>
              <div class="text-xs" :class="caseItem.pass ? 'text-green-500' : 'text-red-500'">{{ caseItem.pass ? '通过' : '不通过' }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const chartData = [65, 78, 52, 90, 73, 85, 68]

const agentRanking = [
  { id: 'evidence', name: '证据分析师', successRate: 98.5 },
  { id: 'discretion', name: '裁量计算师', successRate: 97.2 },
  { id: 'normative', name: '规范性审查员', successRate: 96.8 },
  { id: 'legality', name: '合法性审查员', successRate: 94.2 },
  { id: 'document', name: '文书审计员', successRate: 93.1 },
]

const recentCases = [
  { id: 1, name: '案卷2024-001', time: '10分钟前', score: 89.5, pass: true },
  { id: 2, name: '案卷2024-002', time: '25分钟前', score: 76.3, pass: true },
  { id: 3, name: '案卷2024-003', time: '1小时前', score: 95.0, pass: true },
  { id: 4, name: '案卷2024-004', time: '2小时前', score: 58.2, pass: false },
]
</script>
