<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-2xl font-bold text-gray-800">案卷管理</h2>
        <p class="text-gray-500 mt-1">管理和归档所有案卷评查记录</p>
      </div>
      <div class="flex items-center gap-3">
        <button class="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16h-2v-6a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V16h-2v-3.586l-2.293 2.293M7 16h2.586l2-2H14M7 16h2c.266 0 .52-.097.707-.293l3-3c.187-.187.293-.441.293-.707V10c0-.552-.448-1-1-1H7c-.552 0-1 .448-1 1v6z"></path>
          </svg>
          上传案卷
        </button>
        <button class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          导出
        </button>
      </div>
    </div>
    
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="flex items-center gap-2 p-4 border-b border-gray-200">
        <div 
          v-for="tab in tabs" 
          :key="tab.id"
          class="px-4 py-2 rounded-lg cursor-pointer transition-colors"
          :class="activeTab === tab.id ? 'bg-primary-500 text-white' : 'text-gray-600 hover:bg-gray-100'"
          @click="activeTab = tab.id"
        >
          <span class="flex items-center gap-2">
            {{ tab.icon }}
            {{ tab.name }}
            <span v-if="tab.count" class="px-2 py-0.5 text-xs rounded-full" :class="activeTab === tab.id ? 'bg-white/20' : 'bg-gray-200'">{{ tab.count }}</span>
          </span>
        </div>
      </div>
      
      <div class="p-4">
        <div class="flex items-center justify-between mb-4">
          <div class="relative">
            <input 
              type="text" 
              placeholder="搜索案卷编号、案件名称..." 
              class="w-80 pl-10 pr-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-primary-500"
            />
            <svg class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
          </div>
          <div class="flex items-center gap-2">
            <select class="px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-primary-500">
              <option>全部类型</option>
              <option>一般行政处罚</option>
              <option>重大行政处罚</option>
              <option>简易程序</option>
            </select>
            <select class="px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-primary-500">
              <option>全部时间</option>
              <option>本周</option>
              <option>本月</option>
              <option>本季度</option>
            </select>
          </div>
        </div>
        
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="bg-gray-50">
                <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">案卷编号</th>
                <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">案件名称</th>
                <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">当事人</th>
                <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">评查状态</th>
                <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">综合得分</th>
                <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">评查日期</th>
                <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="caseItem in cases" :key="caseItem.id" class="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <td class="px-4 py-4">
                  <div class="font-medium text-gray-800">{{ caseItem.caseNumber }}</div>
                  <div class="text-xs text-gray-500">{{ caseItem.fileCount }}个文件</div>
                </td>
                <td class="px-4 py-4 text-gray-700">{{ caseItem.name }}</td>
                <td class="px-4 py-4 text-gray-600">{{ caseItem.respondent }}</td>
                <td class="px-4 py-4">
                  <span class="px-3 py-1 text-xs font-medium rounded-full" :class="getStatusClass(caseItem.status)">
                    {{ caseItem.status }}
                  </span>
                </td>
                <td class="px-4 py-4">
                  <div class="font-bold" :class="getScoreClass(caseItem.score)">{{ caseItem.score }}</div>
                  <div class="text-xs" :class="caseItem.pass ? 'text-green-500' : 'text-red-500'">{{ caseItem.pass ? '通过' : '不通过' }}</div>
                </td>
                <td class="px-4 py-4 text-gray-500">{{ caseItem.date }}</td>
                <td class="px-4 py-4">
                  <div class="flex items-center gap-2">
                    <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="查看">
                      <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                      </svg>
                    </button>
                    <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="继续评查">
                      <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                      </svg>
                    </button>
                    <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="收藏">
                      <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div class="flex items-center justify-between mt-6">
          <div class="text-sm text-gray-500">
            共 {{ cases.length }} 条记录，显示第 1-{{ cases.length }} 条
          </div>
          <div class="flex items-center gap-2">
            <button class="px-3 py-1 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">上一页</button>
            <button class="px-3 py-1 text-sm bg-primary-500 text-white rounded-lg">1</button>
            <button class="px-3 py-1 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">2</button>
            <button class="px-3 py-1 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">3</button>
            <button class="px-3 py-1 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">下一页</button>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="selectedCase" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="selectedCase = null">
      <div class="bg-white rounded-xl shadow-2xl w-[90%] max-w-6xl max-h-[90vh] overflow-hidden">
        <div class="flex items-center justify-between p-4 border-b border-gray-200">
          <div>
            <h3 class="font-semibold text-gray-800">{{ selectedCase.caseNumber }}</h3>
            <p class="text-sm text-gray-500">{{ selectedCase.name }}</p>
          </div>
          <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors" @click="selectedCase = null">
            <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div class="h-[calc(90vh-64px)] flex">
          <div class="flex-1 border-r border-gray-200">
            <div class="flex items-center justify-between p-4 border-b border-gray-200">
              <span class="font-medium text-gray-800">原案卷</span>
              <div class="flex items-center gap-2">
                <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                  <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                  </svg>
                </button>
                <span class="text-sm text-gray-600">第 3/23 页</span>
                <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                  <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                  </svg>
                </button>
              </div>
            </div>
            <div class="h-[calc(100%-56px)] bg-gray-100 flex items-center justify-center">
              <div class="text-center text-gray-500">
                <svg class="w-24 h-24 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                </svg>
                <div class="text-lg font-medium">案卷PDF预览</div>
                <div class="text-sm mt-1">{{ selectedCase.caseNumber }}</div>
              </div>
            </div>
          </div>
          <div class="flex-1">
            <div class="flex items-center justify-between p-4 border-b border-gray-200">
              <span class="font-medium text-gray-800">评查报告</span>
              <div class="flex items-center gap-2">
                <button class="px-3 py-1.5 text-sm bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  PDF
                </button>
                <button class="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16h-2v-6a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V16h-2v-3.586l-2.293 2.293M7 16h2.586l2-2H14M7 16h2c.266 0 .52-.097.707-.293l3-3c.187-.187.293-.441.293-.707V10c0-.552-.448-1-1-1H7c-.552 0-1 .448-1 1v6z"></path>
                  </svg>
                  Word
                </button>
              </div>
            </div>
            <div class="h-[calc(100%-56px)] overflow-auto p-6">
              <div class="prose prose-sm max-w-none">
                <div v-html="renderReport()"></div>
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

const activeTab = ref('all')
const selectedCase = ref(null)

const tabs = [
  { id: 'all', name: '全部', icon: '📋', count: 1234 },
  { id: 'pending', name: '待评查', icon: '⏳', count: 12 },
  { id: 'reviewing', name: '评查中', icon: '🔄', count: 3 },
  { id: 'completed', name: '已完成', icon: '✅', count: 156 },
  { id: 'archived', name: '已归档', icon: '📦', count: 890 },
]

const cases = ref([
  { id: 1, caseNumber: '案卷2024-001', name: '某公司超标排放案', respondent: '某环保科技有限公司', status: '已完成', score: 89.5, pass: true, date: '2024-05-15', fileCount: 3 },
  { id: 2, caseNumber: '案卷2024-002', name: '某厂固废倾倒案', respondent: '某化工集团', status: '评查中', score: null, pass: null, date: '2024-05-15', fileCount: 5 },
  { id: 3, caseNumber: '案卷2024-003', name: '某厂噪声超标案', respondent: '某机械制造公司', status: '已完成', score: 95.0, pass: true, date: '2024-05-14', fileCount: 2 },
  { id: 4, caseNumber: '案卷2024-004', name: '某养殖场污染案', respondent: '某生态养殖有限公司', status: '已完成', score: 76.3, pass: true, date: '2024-05-14', fileCount: 4 },
  { id: 5, caseNumber: '案卷2024-005', name: '某工地扬尘污染案', respondent: '某建筑工程公司', status: '待评查', score: null, pass: null, date: '2024-05-13', fileCount: 2 },
  { id: 6, caseNumber: '案卷2024-006', name: '某企业违法排污案', respondent: '某能源科技有限公司', status: '已完成', score: 58.2, pass: false, date: '2024-05-12', fileCount: 6 },
])

const getStatusClass = (status: string) => {
  switch(status) {
    case '待评查': return 'bg-yellow-100 text-yellow-700'
    case '评查中': return 'bg-blue-100 text-blue-700'
    case '已完成': return 'bg-green-100 text-green-700'
    case '已归档': return 'bg-gray-100 text-gray-700'
    default: return 'bg-gray-100 text-gray-700'
  }
}

const getScoreClass = (score: number | null) => {
  if (!score) return 'text-gray-400'
  if (score >= 90) return 'text-green-600'
  if (score >= 80) return 'text-blue-600'
  if (score >= 60) return 'text-yellow-600'
  return 'text-red-600'
}

const renderReport = () => {
  const content = `
# 生态环境行政处罚案卷评查报告

## 基本信息

| 项目 | 内容 |
|------|------|
| 案号 | ${selectedCase.value?.caseNumber} |
| 案件名称 | ${selectedCase.value?.name} |
| 当事人 | ${selectedCase.value?.respondent} |
| 评查日期 | ${selectedCase.value?.date} |

## 评查结论

### 综合得分
**${selectedCase.value?.score || '待评查'} 分**

### 评查等级
${selectedCase.value?.score >= 90 ? '优秀' : selectedCase.value?.score >= 80 ? '良好' : selectedCase.value?.score >= 60 ? '合格' : '不合格'}

### 是否通过
${selectedCase.value?.pass ? '✅ 通过' : '❌ 不通过'}

## 合法性审查

### 一票否决情况
- 是否触发否决：${selectedCase.value?.pass ? '✅ 否' : '❌ 是'}
- 合法性得分：${selectedCase.value?.pass ? 50 : 0} 分

## 规范性评分

### 评分详情
| 项目 | 得分 |
|------|------|
| 文书得分 | ${selectedCase.value?.score ? Math.round(selectedCase.value.score * 0.8) : 0}/100 |
| 基本要素 | ${selectedCase.value?.score ? Math.round(selectedCase.value.score * 0.2) : 0}/20 |

## 改进建议

1. 继续保持当前评查质量
2. 建议定期开展案卷评查培训
3. 加强文书规范化管理

---

**评查人**: 系统自动评查  
**生成时间**: ${new Date().toLocaleString()}  
**系统版本**: v1.0.0
`
  return md.render(content)
}
</script>
