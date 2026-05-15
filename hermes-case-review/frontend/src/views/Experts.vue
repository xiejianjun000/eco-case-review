<template>
  <div class="p-6">
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-gray-800">专家团队</h2>
      <p class="text-gray-500 mt-1">管理和配置您的智能评查团队</p>
    </div>
    
    <div class="grid grid-cols-6 gap-4 mb-6">
      <div 
        v-for="agent in agents" 
        :key="agent.id"
        class="agent-card bg-white rounded-xl p-4 border-2 cursor-pointer transition-all"
        :class="selectedAgent?.id === agent.id ? 'border-primary-500 shadow-lg' : 'border-gray-100 hover:border-primary-200'"
        @click="selectAgent(agent)"
      >
        <div class="text-4xl text-center mb-3">{{ agent.avatar }}</div>
        <div class="text-center">
          <div class="font-semibold text-gray-800">{{ agent.name }}</div>
          <div class="text-xs text-gray-500 mt-1">{{ agent.nameEn }}</div>
          <div class="flex items-center justify-center gap-1 mt-2">
            <span class="w-2 h-2 rounded-full" :class="getStatusDotClass(agent.status)"></span>
            <span class="text-xs" :class="getStatusTextClass(agent.status)">{{ getStatusText(agent.status) }}</span>
          </div>
        </div>
        <div class="mt-3 pt-3 border-t border-gray-100">
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-500">今日任务</span>
            <span class="font-medium text-gray-800">{{ agent.todayTasks }}</span>
          </div>
          <div class="flex items-center justify-between text-sm mt-1">
            <span class="text-gray-500">成功率</span>
            <span class="font-medium text-green-600">{{ agent.successRate }}%</span>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="selectedAgent" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="bg-gradient-to-r from-primary-500 to-primary-600 p-6 text-white">
        <div class="flex items-start gap-4">
          <div class="w-16 h-16 bg-white/20 rounded-xl flex items-center justify-center text-3xl">
            {{ selectedAgent.avatar }}
          </div>
          <div class="flex-1">
            <h3 class="text-xl font-bold">{{ selectedAgent.name }}</h3>
            <div class="text-white/80 mt-1">{{ selectedAgent.nameEn }}</div>
            <div class="flex items-center gap-3 mt-2">
              <span class="px-2 py-0.5 bg-white/20 rounded text-xs">
                {{ getStatusText(selectedAgent.status) }}
              </span>
              <span class="px-2 py-0.5 bg-white/20 rounded text-xs">
                今日任务: {{ selectedAgent.todayTasks }}
              </span>
              <span class="px-2 py-0.5 bg-green-400 rounded text-xs">
                成功率: {{ selectedAgent.successRate }}%
              </span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button class="p-2 hover:bg-white/10 rounded-lg transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
            </button>
            <button class="p-2 hover:bg-white/10 rounded-lg transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </button>
            <button class="p-2 hover:bg-white/10 rounded-lg transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
            </button>
          </div>
        </div>
        <p class="mt-4 text-white/90">{{ selectedAgent.description }}</p>
      </div>
      
      <div class="p-6">
        <h4 class="text-lg font-semibold text-gray-800 mb-4">五大核心配置 ⭐</h4>
        <div class="grid grid-cols-5 gap-4">
          <div 
            v-for="config in configs" 
            :key="config.id"
            class="bg-gray-50 rounded-xl p-4 cursor-pointer hover:bg-gray-100 transition-colors"
            :class="activeConfig === config.id ? 'ring-2 ring-primary-500' : ''"
            @click="selectConfig(config.id)"
          >
            <div class="text-3xl text-center mb-2">{{ config.icon }}</div>
            <div class="text-center">
              <div class="font-medium text-gray-800">{{ config.name }}</div>
              <div class="text-xs text-gray-500 mt-1">{{ config.size }}</div>
            </div>
          </div>
        </div>
        
        <div class="mt-6">
          <div class="flex items-center justify-between mb-4">
            <h5 class="font-semibold text-gray-800">{{ getCurrentConfigName() }}</h5>
            <button class="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm">
              编辑配置
            </button>
          </div>
          <div class="bg-gray-50 rounded-xl p-6 min-h-[400px]">
            <div class="prose prose-sm max-w-none">
              <div v-html="renderConfigContent()"></div>
            </div>
          </div>
        </div>
        
        <div class="mt-6 pt-6 border-t border-gray-200">
          <div class="flex items-center justify-between">
            <div>
              <h5 class="font-semibold text-gray-800">今日学习情况</h5>
              <p class="text-sm text-gray-500 mt-1">智能体每日进化记录</p>
            </div>
            <div class="flex items-center gap-4">
              <div class="text-center">
                <div class="text-2xl font-bold text-green-500">45</div>
                <div class="text-xs text-gray-500">👍 好评 (+3)</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-red-500">2</div>
                <div class="text-xs text-gray-500">👎 差评 (-1)</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-primary-500">12</div>
                <div class="text-xs text-gray-500">📚 知识更新</div>
              </div>
            </div>
          </div>
          
          <div class="mt-4">
            <h6 class="font-medium text-gray-700 mb-3">学习历史</h6>
            <div class="space-y-2">
              <div v-for="(record, index) in learningHistory" :key="index" class="flex items-center justify-between p-3 bg-white rounded-lg">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full flex items-center justify-center" :class="record.type === 'praise' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'">
                    {{ record.type === 'praise' ? '👍' : '👎' }}
                  </div>
                  <div>
                    <div class="font-medium text-gray-800">{{ record.title }}</div>
                    <div class="text-xs text-gray-500">{{ record.date }}</div>
                  </div>
                </div>
                <span class="text-xs px-2 py-1 rounded-full" :class="record.type === 'praise' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
                  {{ record.type === 'praise' ? '已优化' : '待改进' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import markdownIt from 'markdown-it'

const md = markdownIt()

const agents = ref([
  { id: 'legality', name: '合法性审查员', nameEn: 'Legality Reviewer', status: 'running', todayTasks: 12, successRate: 98.5, description: '精通《行政处罚法》，负责检查25项一票否决条件，确保处罚决定合法合规', avatar: '⚖️' },
  { id: 'normative', name: '规范性审查员', nameEn: 'Normative Reviewer', status: 'idle', todayTasks: 8, successRate: 96.8, description: '文书专家，负责卷面要素和文书质量评分，提升案卷规范化水平', avatar: '📋' },
  { id: 'discretion', name: '裁量计算师', nameEn: 'Discretion Calculator', status: 'running', todayTasks: 5, successRate: 97.2, description: '精算专家，负责罚款金额裁量计算，确保过罚相当', avatar: '🧮' },
  { id: 'evidence', name: '证据分析师', nameEn: 'Evidence Analyst', status: 'idle', todayTasks: 3, successRate: 95.5, description: '证据专家，负责证据链三性分析（合法性、关联性、客观性）', avatar: '🔍' },
  { id: 'document', name: '文书审计员', nameEn: 'Document Auditor', status: 'running', todayTasks: 7, successRate: 94.2, description: '审计专家，负责文书完整性检查，确保必备文书齐全', avatar: '📄' },
  { id: 'comprehensive', name: '综合评估师', nameEn: 'Comprehensive Evaluator', status: 'idle', todayTasks: 2, successRate: 93.1, description: '评估专家，负责综合评分和报告生成，提供专业评查结论', avatar: '📊' },
])

const selectedAgent = ref(agents.value[0])
const activeConfig = ref('soul')

const configs = [
  { id: 'soul', name: '灵魂', icon: '👁️', size: '0.5KB' },
  { id: 'memory', name: '记忆', icon: '🧠', size: '2.3KB' },
  { id: 'skills', name: '技能', icon: '⚡', size: '1.8KB' },
  { id: 'tools', name: '工具', icon: '🔧', size: '1.2KB' },
  { id: 'rules', name: '规则', icon: '📋', size: '2.1KB' },
]

const learningHistory = [
  { type: 'praise', title: '准确识别序号14问题', date: '2024-05-15 14:30', status: 'optimized' },
  { type: 'praise', title: '法律依据引用准确', date: '2024-05-15 10:20', status: 'optimized' },
  { type: 'criticism', title: '序号10误判', date: '2024-05-14 16:45', status: 'pending' },
  { type: 'praise', title: '程序违法判断准确', date: '2024-05-14 09:15', status: 'optimized' },
]

const selectAgent = (agent: any) => {
  selectedAgent.value = agent
}

const selectConfig = (configId: string) => {
  activeConfig.value = configId
}

const getStatusDotClass = (status: string) => {
  if (status === 'running') return 'bg-green-500'
  if (status === 'idle') return 'bg-gray-400'
  return 'bg-yellow-500'
}

const getStatusTextClass = (status: string) => {
  if (status === 'running') return 'text-green-600'
  if (status === 'idle') return 'text-gray-500'
  return 'text-yellow-600'
}

const getStatusText = (status: string) => {
  if (status === 'running') return '运行中'
  if (status === 'idle') return '空闲'
  return '等待中'
}

const getCurrentConfigName = () => {
  const config = configs.find(c => c.id === activeConfig.value)
  return config?.name || ''
}

const renderConfigContent = () => {
  const content = `
## ${getCurrentConfigName()}配置

### 配置说明

这是智能体的${getCurrentConfigName()}配置文件，定义了智能体的${getCurrentConfigName()}核心属性。

### 当前内容

\`\`\`yaml
name: ${selectedAgent.value.name}
type: ${activeConfig.value}
version: v1.0
last_updated: 2024-05-15
description: ${selectedAgent.value.description}
\`\`\`

### 配置要点

- **核心功能**: 智能体的${getCurrentConfigName()}能力定义
- **配置项**: 可根据业务需求进行调整
- **版本管理**: 支持版本控制和回滚

### 编辑建议

请在编辑前仔细阅读配置说明，确保修改符合业务规则。
`
  return md.render(content)
}
</script>
