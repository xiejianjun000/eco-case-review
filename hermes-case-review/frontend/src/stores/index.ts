import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  const currentCase = ref(null)
  const reviewStatus = ref<'idle' | 'reviewing' | 'completed'>('idle')
  const messages = ref<Array<{ id: number; type: 'user' | 'agent'; content: string; agentName?: string; timestamp: Date }>>([])
  const currentModel = ref('DeepSeek-V3')
  const showRightPanel = ref(true)

  const addMessage = (type: 'user' | 'agent', content: string, agentName?: string) => {
    messages.value.push({
      id: Date.now(),
      type,
      content,
      agentName,
      timestamp: new Date(),
    })
  }

  const startReview = (caseData: any) => {
    currentCase.value = caseData
    reviewStatus.value = 'reviewing'
  }

  const completeReview = () => {
    reviewStatus.value = 'completed'
  }

  const resetReview = () => {
    currentCase.value = null
    reviewStatus.value = 'idle'
    messages.value = []
  }

  const toggleRightPanel = () => {
    showRightPanel.value = !showRightPanel.value
  }

  return {
    currentCase,
    reviewStatus,
    messages,
    currentModel,
    showRightPanel,
    addMessage,
    startReview,
    completeReview,
    resetReview,
    toggleRightPanel,
  }
})

export const useAgentStore = defineStore('agent', () => {
  const agents = ref([
    {
      id: 'legality',
      name: '合法性审查员',
      nameEn: 'Legality Reviewer',
      status: 'running',
      todayTasks: 12,
      successRate: 98.5,
      description: '精通《行政处罚法》，负责检查25项一票否决条件',
      avatar: '⚖️',
    },
    {
      id: 'normative',
      name: '规范性审查员',
      nameEn: 'Normative Reviewer',
      status: 'idle',
      todayTasks: 8,
      successRate: 96.8,
      description: '文书专家，负责卷面要素和文书质量评分',
      avatar: '📋',
    },
    {
      id: 'discretion',
      name: '裁量计算师',
      nameEn: 'Discretion Calculator',
      status: 'running',
      todayTasks: 5,
      successRate: 97.2,
      description: '精算专家，负责罚款金额裁量计算',
      avatar: '🧮',
    },
    {
      id: 'evidence',
      name: '证据分析师',
      nameEn: 'Evidence Analyst',
      status: 'idle',
      todayTasks: 3,
      successRate: 95.5,
      description: '证据专家，负责证据链三性分析',
      avatar: '🔍',
    },
    {
      id: 'document',
      name: '文书审计员',
      nameEn: 'Document Auditor',
      status: 'running',
      todayTasks: 7,
      successRate: 94.2,
      description: '审计专家，负责文书完整性检查',
      avatar: '📄',
    },
    {
      id: 'comprehensive',
      name: '综合评估师',
      nameEn: 'Comprehensive Evaluator',
      status: 'idle',
      todayTasks: 2,
      successRate: 93.1,
      description: '评估专家，负责综合评分和报告生成',
      avatar: '📊',
    },
  ])

  const selectedAgent = ref(null)

  const getAgentById = (id: string) => {
    return agents.value.find(a => a.id === id)
  }

  const selectAgent = (agentId: string) => {
    selectedAgent.value = getAgentById(agentId)
  }

  const updateAgentStatus = (agentId: string, status: string) => {
    const agent = getAgentById(agentId)
    if (agent) {
      agent.status = status
    }
  }

  return {
    agents,
    selectedAgent,
    getAgentById,
    selectAgent,
    updateAgentStatus,
  }
})
