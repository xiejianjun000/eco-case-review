<template>
  <div class="p-6 h-full flex flex-col">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-2xl font-bold text-gray-800">审查交流</h2>
        <p class="text-gray-500 mt-1">与专业智能体团队进行案件审查交流</p>
      </div>
      <div class="flex items-center gap-3">
        <button 
          @click="resetChat"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          重置对话
        </button>
        <button 
          @click="startNewReview"
          class="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
          </svg>
          开始新审查
        </button>
      </div>
    </div>

    <div class="flex gap-6 flex-1 overflow-hidden">
      <!-- 左侧：智能体选择 -->
      <div class="w-72 bg-white rounded-xl border border-gray-200 flex flex-col overflow-hidden">
        <div class="p-4 border-b border-gray-200">
          <h3 class="font-semibold text-gray-800">专业智能体</h3>
        </div>
        <div class="flex-1 overflow-y-auto p-2 space-y-2">
          <div
            v-for="agent in agents"
            :key="agent.id"
            @click="selectAgent(agent)"
            class="p-3 rounded-lg cursor-pointer transition-all border-2"
            :class="
              selectedAgent?.id === agent.id
                ? 'border-primary-500 bg-primary-50'
                : 'border-transparent hover:bg-gray-50'
            "
          >
            <div class="flex items-center gap-3">
              <div class="text-2xl">{{ agent.avatar }}</div>
              <div class="flex-1">
                <div class="font-medium text-gray-800">{{ agent.name }}</div>
                <div class="text-xs text-gray-500">{{ agent.nameEn }}</div>
              </div>
              <div class="flex items-center gap-1">
                <span class="w-2 h-2 rounded-full" :class="getStatusDotClass(agent.status)"></span>
              </div>
            </div>
            <div class="mt-2 text-xs text-gray-600 line-clamp-2">
              {{ agent.description }}
            </div>
          </div>
        </div>
      </div>

      <!-- 中间：对话区域 -->
      <div class="flex-1 bg-white rounded-xl border border-gray-200 flex flex-col overflow-hidden">
        <!-- 对话头部 -->
        <div class="p-4 border-b border-gray-200 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center text-xl">
              {{ selectedAgent?.avatar || '🤖' }}
            </div>
            <div>
              <div class="font-medium text-gray-800">
                {{ selectedAgent?.name || '选择智能体' }}
              </div>
              <div class="text-xs text-gray-500 flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full" :class="getStatusDotClass(selectedAgent?.status || 'idle')"></span>
                {{ getStatusText(selectedAgent?.status || 'idle') }}
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="语音通话">
              <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
              </svg>
            </button>
            <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="查看历史">
              <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- 对话消息 -->
        <div class="flex-1 overflow-y-auto p-4 space-y-4" ref="messagesContainer">
          <div v-if="messages.length === 0" class="h-full flex items-center justify-center">
            <div class="text-center text-gray-500">
              <div class="text-5xl mb-4">💬</div>
              <div class="text-lg font-medium text-gray-700">开始新的审查交流</div>
              <div class="text-sm mt-2">选择左侧智能体，开始专业案件审查</div>
            </div>
          </div>

          <div
            v-for="message in messages"
            :key="message.id"
            class="flex gap-3"
            :class="message.type === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div v-if="message.type === 'agent'" class="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
              {{ getAgentAvatar(message.agentId) }}
            </div>
            <div class="max-w-[70%]">
              <div
                class="rounded-2xl px-4 py-3"
                :class="
                  message.type === 'user'
                    ? 'bg-primary-500 text-white rounded-tr-none'
                    : 'bg-gray-100 text-gray-800 rounded-tl-none'
                "
              >
                <div v-if="message.agentName && message.type === 'agent'" class="text-xs font-medium mb-1 opacity-80">
                  {{ message.agentName }}
                </div>
                <div class="whitespace-pre-wrap" v-html="renderMarkdown(message.content)"></div>
              </div>
              <div class="text-xs text-gray-400 mt-1 text-right">
                {{ formatTime(message.timestamp) }}
              </div>
            </div>
            <div v-if="message.type === 'user'" class="w-8 h-8 bg-gray-200 rounded-lg flex items-center justify-center flex-shrink-0">
              👤
            </div>
          </div>

          <div v-if="isTyping" class="flex gap-3">
            <div class="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
              {{ getAgentAvatar(selectedAgent?.id) }}
            </div>
            <div class="bg-gray-100 rounded-2xl rounded-tl-none px-4 py-3">
              <div class="flex gap-1">
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="p-4 border-t border-gray-200">
          <div class="flex items-end gap-3">
            <div class="flex gap-2">
              <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="上传文件">
                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7.172l-4.832 4.83a2 2 0 00.001 2.827l.001.001a2 2 0 002.828.002l4.83-4.83a6 6 0 00-8.484-8.484l-4.83 4.83a10 10 0 0014.142 14.142l4.83-4.83a6 6 0 00-8.485-8.485z"/>
                </svg>
              </button>
              <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="快速提问">
                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </button>
            </div>
            <div class="flex-1 relative">
              <textarea
                v-model="inputMessage"
                @keydown.enter.prevent="sendMessage"
                placeholder="输入您的问题或描述案件..."
                class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:border-primary-500 resize-none"
                rows="1"
              ></textarea>
            </div>
            <button
              @click="sendMessage"
              :disabled="!inputMessage.trim() || !selectedAgent"
              class="p-3 bg-primary-500 text-white rounded-xl hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
              </svg>
            </button>
          </div>

          <div class="mt-3 flex gap-2 flex-wrap">
            <button
              v-for="suggestion in quickSuggestions"
              :key="suggestion"
              @click="useSuggestion(suggestion)"
              class="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              {{ suggestion }}
            </button>
          </div>
        </div>
      </div>

      <!-- 右侧：案件信息 -->
      <div class="w-80 bg-white rounded-xl border border-gray-200 flex flex-col overflow-hidden">
        <div class="p-4 border-b border-gray-200">
          <h3 class="font-semibold text-gray-800">案件信息</h3>
        </div>
        <div class="flex-1 overflow-y-auto p-4 space-y-4">
          <div v-if="currentCase" class="space-y-4">
            <div class="bg-gray-50 rounded-lg p-3">
              <div class="text-sm text-gray-500 mb-1">案卷编号</div>
              <div class="font-medium text-gray-800">{{ currentCase.caseNumber }}</div>
            </div>

            <div class="bg-gray-50 rounded-lg p-3">
              <div class="text-sm text-gray-500 mb-1">案件名称</div>
              <div class="font-medium text-gray-800">{{ currentCase.name }}</div>
            </div>

            <div class="bg-gray-50 rounded-lg p-3">
              <div class="text-sm text-gray-500 mb-1">当事人</div>
              <div class="font-medium text-gray-800">{{ currentCase.respondent }}</div>
            </div>

            <div class="bg-gray-50 rounded-lg p-3">
              <div class="text-sm text-gray-500 mb-1">案件类型</div>
              <div class="font-medium text-gray-800">{{ currentCase.caseType }}</div>
            </div>

            <div class="bg-gray-50 rounded-lg p-3">
              <div class="text-sm text-gray-500 mb-1">违法事实</div>
              <div class="text-sm text-gray-700">{{ currentCase.violation }}</div>
            </div>

            <div v-if="currentCase.score" class="bg-gray-50 rounded-lg p-3">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm text-gray-500">综合评分</span>
                <span class="text-2xl font-bold" :class="getScoreClass(currentCase.score)">
                  {{ currentCase.score }}
                </span>
              </div>
              <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full"
                  :class="getScoreClass(currentCase.score)"
                  :style="{ width: currentCase.score + '%' }"
                ></div>
              </div>
              <div class="text-xs text-center mt-2" :class="getScoreClass(currentCase.score)">
                {{ currentCase.pass ? '✅ 审查通过' : '❌ 审查不通过' }}
              </div>
            </div>

            <div class="border-t border-gray-200 pt-4">
              <h4 class="font-medium text-gray-800 mb-3">审查进度</h4>
              <div class="space-y-2">
                <div
                  v-for="(step, index) in reviewSteps"
                  :key="index"
                  class="flex items-center gap-3"
                >
                  <div class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium"
                    :class="step.status === 'completed' ? 'bg-green-500 text-white' : step.status === 'in-progress' ? 'bg-primary-500 text-white animate-pulse' : 'bg-gray-200 text-gray-500'"
                  >
                    {{ step.status === 'completed' ? '✓' : index + 1 }}
                  </div>
                  <div class="flex-1">
                    <div class="text-sm font-medium text-gray-800">{{ step.name }}</div>
                    <div class="text-xs text-gray-500">{{ step.description }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="text-center text-gray-500 py-8">
            <div class="text-4xl mb-3">📁</div>
            <div class="text-lg font-medium text-gray-700">选择案件</div>
            <div class="text-sm mt-2">从案卷管理中选择案件开始审查</div>
            <button class="mt-4 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm">
              选择案件
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import { useAppStore } from '../stores'
import markdownIt from 'markdown-it'

const appStore = useAppStore()
const md = markdownIt()

const agents = ref([
  {
    id: 'legality',
    name: '合法性审查员',
    nameEn: 'Legality Reviewer',
    status: 'running',
    todayTasks: 12,
    successRate: 98.5,
    description: '精通《行政处罚法》，负责检查25项一票否决条件',
    avatar: '⚖️'
  },
  {
    id: 'normative',
    name: '规范性审查员',
    nameEn: 'Normative Reviewer',
    status: 'idle',
    todayTasks: 8,
    successRate: 96.8,
    description: '文书专家，负责卷面要素和文书质量评分',
    avatar: '📋'
  },
  {
    id: 'discretion',
    name: '裁量计算师',
    nameEn: 'Discretion Calculator',
    status: 'running',
    todayTasks: 5,
    successRate: 97.2,
    description: '精算专家，负责罚款金额裁量计算',
    avatar: '🧮'
  },
  {
    id: 'evidence',
    name: '证据分析师',
    nameEn: 'Evidence Analyst',
    status: 'idle',
    todayTasks: 3,
    successRate: 95.5,
    description: '证据专家，负责证据链三性分析',
    avatar: '🔍'
  },
  {
    id: 'document',
    name: '文书审计员',
    nameEn: 'Document Auditor',
    status: 'running',
    todayTasks: 7,
    successRate: 94.2,
    description: '审计专家，负责文书完整性检查',
    avatar: '📄'
  },
  {
    id: 'comprehensive',
    name: '综合评估师',
    nameEn: 'Comprehensive Evaluator',
    status: 'idle',
    todayTasks: 2,
    successRate: 93.1,
    description: '评估专家，负责综合评分和报告生成',
    avatar: '📊'
  }
])

const selectedAgent = ref<any>(null)
const messages = ref<any[]>([])
const inputMessage = ref('')
const isTyping = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)

const currentCase = ref({
  caseNumber: '案例2024-001',
  name: '某食品有限公司篡改自动监测数据排放水污染物案',
  respondent: '某食品有限公司',
  caseType: '水污染防治类',
  violation: '2024年5月检查发现，该公司在线监测设备COD和氨氮的校准参数多次被人为修改，不符合斜率k=1、截距b=0的设备管理要求，导致在线监测结果失真。',
  score: 76.5,
  pass: true
})

const reviewSteps = ref([
  { name: '合法性审查', description: '检查25项否决条件', status: 'completed' },
  { name: '规范性评分', description: '文书质量评估', status: 'completed' },
  { name: '证据链分析', description: '证据三性验证', status: 'in-progress' },
  { name: '裁量计算', description: '罚款金额建议', status: 'pending' },
  { name: '综合评估', description: '生成审查报告', status: 'pending' }
])

const quickSuggestions = [
  '请分析本案的法律适用问题',
  '检查证据链是否完整',
  '给出处罚裁量建议',
  '本案有哪些风险点',
  '需要补充哪些材料'
]

const getStatusDotClass = (status: string) => {
  if (status === 'running') return 'bg-green-500'
  if (status === 'idle') return 'bg-gray-400'
  return 'bg-yellow-500'
}

const getStatusText = (status: string) => {
  if (status === 'running') return '在线可用'
  if (status === 'idle') return '空闲中'
  return '忙碌中'
}

const getScoreClass = (score: number) => {
  if (score >= 90) return 'text-green-600'
  if (score >= 80) return 'text-blue-600'
  if (score >= 60) return 'text-yellow-600'
  return 'text-red-600'
}

const getAgentAvatar = (agentId?: string) => {
  if (!agentId) return '🤖'
  const agent = agents.value.find(a => a.id === agentId)
  return agent?.avatar || '🤖'
}

const selectAgent = (agent: any) => {
  selectedAgent.value = agent
  if (messages.value.length === 0) {
    addMessage('agent', `您好！我是${agent.name}，${agent.description}。请告诉我您需要什么帮助？`, agent.id, agent.name)
  }
}

const addMessage = (type: 'user' | 'agent', content: string, agentId?: string, agentName?: string) => {
  messages.value.push({
    id: Date.now(),
    type,
    content,
    agentId,
    agentName,
    timestamp: new Date()
  })
  scrollToBottom()
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || !selectedAgent.value) return

  const userMessage = inputMessage.value
  addMessage('user', userMessage)
  inputMessage.value = ''
  isTyping.value = true

  await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1500))

  let response = ''
  switch (selectedAgent.value.id) {
    case 'legality':
      response = `针对您的问题，我从合法性角度分析如下：

**关键法律条款检查：**

1. **《中华人民共和国行政处罚法》第三十九条** ✓
   - 当事人享有的陈述权、申辩权已告知

2. **《环境行政处罚办法》第二十八条** ✓
   - 违法事实清楚，证据充分

3. **《行政处罚法》第四十二条** ✓
   - 听证程序适用正确

**一票否决条件检查：**
✅ 未发现25项否决情形

请问还需要检查其他方面吗？`
      break
    case 'normative':
      response = `从规范性角度评估：

**文书评分结果：**
- 立案审批表：92分 ✓
- 调查询问笔录：88分 ✓
- 现场检查（勘验）笔录：90分 ✓
- 处罚告知书：85分 ✓
- 处罚决定书：89分 ✓

**卷面要素检查：**
✅ 当事人基本信息完整
✅ 违法事实描述清楚
✅ 法律依据引用准确
✅ 处罚裁量幅度适当
✅ 文书送达回证规范

**扣分项目：**
- 询问笔录缺少执法人员签名确认 ➝ -3分
- 现场照片缺少拍摄时间标注 ➝ -2分

需要我详细说明扣分依据吗？`
      break
    case 'evidence':
      response = `正在分析本案的证据链完整性...

**证据清单分析：**

1. **现场检查（勘验）笔录** ✅
   - 时间、地点、当事人签字齐全
   - 现场情况记载详实

2. **调查询问笔录** ✅
   - 法定代表人询问完整
   - 关键事实确认清楚

3. **监测报告** ✅
   - CMA资质认证有效
   - 监测方法符合标准
   - 数据来源可追溯

4. **现场照片/录像** ⚠️
   - 缺少拍摄时间戳标记
   - 建议补充GPS定位信息

5. **物证** ✅
   - 涉案设备查封扣押清单齐全

**证据链三性评估：**
- 合法性：92分 ✓
- 关联性：88分 ✓
- 真实性：85分 ✓

总体评估：证据链基本完整，建议补充完善照片资料。`
      break
    case 'discretion':
      response = `根据本案情节，我来进行处罚裁量计算：

**案件基本情况：**
- 违法行为：篡改自动监测数据
- 适用法律：《水污染防治法》第三十九条
- 违法持续时间：2023年12月至2024年5月（6个月）

**裁量参考因素：**

1. **违法情节严重程度** - 较重
   - 故意篡改数据
   - 持续时间较长

2. **改正态度** - 一般
   - 配合调查
   - 已停止违法行为

3. **环境影响程度** - 中等
   - 未造成重大污染事故
   - 但数据失真影响监管

**处罚裁量建议：**
- **基准罚款：** 20万元
- **从重情节：** +30% → +6万元
- **配合调查：** -10% → -2万元
- **最终建议罚款：** 24万元

**法律依据：**
《水污染防治法》第八十二条、《生态环境行政处罚裁量基准（试行）》

是否需要调整裁量幅度？`
      break
    default:
      response = `感谢您的提问。我正在分析您的问题，请稍候...

作为${selectedAgent.value.name}，我可以为您提供以下帮助：
- 案件综合评估
- 法律问题咨询
- 证据链分析
- 处罚裁量建议

请告诉我您具体需要什么帮助？`
  }

  isTyping.value = false
  addMessage('agent', response, selectedAgent.value.id, selectedAgent.value.name)
}

const useSuggestion = (suggestion: string) => {
  inputMessage.value = suggestion
}

const resetChat = () => {
  messages.value = []
}

const startNewReview = () => {
  resetChat()
  const greeting = `我已准备好协助您进行案件审查。请问您需要进行哪方面的审查工作？

建议步骤：
1. 📋 上传或选择案卷
2. ⚖️ 合法性审查
3. 📊 规范性评分
4. 📝 综合评估
5. 📄 生成报告`

  addMessage('agent', greeting, 'comprehensive', '综合评估师')
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const renderMarkdown = (content: string) => {
  return md.render(content)
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

onMounted(() => {
  selectedAgent.value = agents.value[0]
  startNewReview()
})
</script>

<style scoped>
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
