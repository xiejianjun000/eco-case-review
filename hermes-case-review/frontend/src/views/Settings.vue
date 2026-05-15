<template>
  <div class="p-6">
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-gray-800">配置管理</h2>
      <p class="text-gray-500 mt-1">管理系统设置和智能体配置</p>
    </div>
    
    <div class="grid grid-cols-3 gap-4 mb-6">
      <div 
        v-for="tab in tabs" 
        :key="tab.id"
        class="bg-white rounded-xl p-4 border-2 cursor-pointer transition-all"
        :class="activeTab === tab.id ? 'border-primary-500 shadow-lg' : 'border-gray-100 hover:border-gray-200'"
        @click="activeTab = tab.id"
      >
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-xl flex items-center justify-center" :class="activeTab === tab.id ? 'bg-primary-100' : 'bg-gray-100'">
            <component :is="tab.icon" class="w-6 h-6" :class="activeTab === tab.id ? 'text-primary-600' : 'text-gray-600'" />
          </div>
          <div>
            <div class="font-semibold text-gray-800">{{ tab.name }}</div>
            <div class="text-sm text-gray-500">{{ tab.description }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div class="flex items-center justify-between mb-6">
        <h3 class="font-semibold text-gray-800">{{ getTabTitle() }}</h3>
        <button class="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm">
          保存设置
        </button>
      </div>
      
      <div v-if="activeTab === 'system'" class="space-y-6">
        <div>
          <h4 class="font-medium text-gray-700 mb-4">基础配置</h4>
          <div class="grid grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-2">系统名称</label>
              <input type="text" value="生态环境案卷评查系统" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-primary-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-2">系统语言</label>
              <select class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-primary-500">
                <option>中文</option>
                <option>English</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-2">时间格式</label>
              <select class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-primary-500">
                <option>YYYY-MM-DD HH:mm:ss</option>
                <option>YYYY/MM/DD HH:mm:ss</option>
                <option>DD/MM/YYYY HH:mm:ss</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-2">日期格式</label>
              <select class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-primary-500">
                <option>YYYY-MM-DD</option>
                <option>YYYY/MM/DD</option>
                <option>DD/MM/YYYY</option>
              </select>
            </div>
          </div>
        </div>
        
        <div>
          <h4 class="font-medium text-gray-700 mb-4">API配置</h4>
          <div class="grid grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-2">DeepSeek API Key</label>
              <input type="password" value="******************" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-primary-500" />
              <button class="mt-2 px-3 py-1 text-sm text-primary-600 hover:text-primary-700">测试连接</button>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-2">GLM API Key</label>
              <input type="password" value="******************" class="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-primary-500" />
              <button class="mt-2 px-3 py-1 text-sm text-primary-600 hover:text-primary-700">测试连接</button>
            </div>
          </div>
        </div>
        
        <div>
          <h4 class="font-medium text-gray-700 mb-4">存储配置</h4>
          <div class="grid grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-2">案卷存储路径</label>
              <div class="flex items-center gap-2">
                <input type="text" value="/data/cases" class="flex-1 px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-primary-500" />
                <button class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">浏览</button>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-2">报告存储路径</label>
              <div class="flex items-center gap-2">
                <input type="text" value="/data/reports" class="flex-1 px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-primary-500" />
                <button class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">浏览</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="activeTab === 'agents'" class="space-y-6">
        <div>
          <h4 class="font-medium text-gray-700 mb-4">智能体设置</h4>
          <div class="space-y-4">
            <div v-for="agent in agentSettings" :key="agent.id" class="bg-gray-50 rounded-xl p-4">
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center text-xl">
                    {{ agent.avatar }}
                  </div>
                  <div>
                    <div class="font-medium text-gray-800">{{ agent.name }}</div>
                    <div class="text-sm text-gray-500">{{ agent.description }}</div>
                  </div>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" :checked="agent.enabled" class="sr-only peer">
                  <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>
              <div class="flex items-center gap-6 text-sm text-gray-500">
                <span>优先级: {{ agent.priority }}</span>
                <span>超时时间: {{ agent.timeout }}s</span>
                <span>重试次数: {{ agent.retries }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="activeTab === 'users'" class="space-y-6">
        <div>
          <div class="flex items-center justify-between mb-4">
            <h4 class="font-medium text-gray-700">用户列表</h4>
            <button class="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm">
              添加用户
            </button>
          </div>
          <table class="w-full">
            <thead>
              <tr class="bg-gray-50">
                <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">用户名</th>
                <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">邮箱</th>
                <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">角色</th>
                <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">状态</th>
                <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id" class="border-b border-gray-100">
                <td class="px-4 py-4">
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                      <span class="text-sm font-medium text-primary-600">{{ user.name.charAt(0) }}</span>
                    </div>
                    <span class="font-medium text-gray-800">{{ user.name }}</span>
                  </div>
                </td>
                <td class="px-4 py-4 text-gray-600">{{ user.email }}</td>
                <td class="px-4 py-4">
                  <span class="px-2 py-1 text-xs rounded-full" :class="user.role === 'admin' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'">{{ user.role === 'admin' ? '管理员' : '普通用户' }}</span>
                </td>
                <td class="px-4 py-4">
                  <span class="px-2 py-1 text-xs rounded-full bg-green-100 text-green-700">启用</span>
                </td>
                <td class="px-4 py-4">
                  <button class="px-3 py-1 text-sm text-primary-600 hover:text-primary-700">编辑</button>
                  <button class="px-3 py-1 text-sm text-red-600 hover:text-red-700 ml-2">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Settings, Users, Cpu } from '@element-plus/icons-vue'

const activeTab = ref('system')

const tabs = [
  { id: 'system', name: '系统设置', description: '基础配置和API设置', icon: Settings },
  { id: 'agents', name: '智能体配置', description: '管理智能体参数', icon: Cpu },
  { id: 'users', name: '用户管理', description: '管理系统用户', icon: Users },
]

const agentSettings = [
  { id: 'legality', name: '合法性审查员', avatar: '⚖️', description: '检查25项一票否决条件', enabled: true, priority: 1, timeout: 60, retries: 2 },
  { id: 'normative', name: '规范性审查员', avatar: '📋', description: '文书质量评分', enabled: true, priority: 2, timeout: 60, retries: 2 },
  { id: 'discretion', name: '裁量计算师', avatar: '🧮', description: '罚款金额计算', enabled: true, priority: 3, timeout: 30, retries: 2 },
  { id: 'evidence', name: '证据分析师', avatar: '🔍', description: '证据链分析', enabled: true, priority: 4, timeout: 60, retries: 2 },
  { id: 'document', name: '文书审计员', avatar: '📄', description: '文书完整性检查', enabled: true, priority: 5, timeout: 30, retries: 2 },
  { id: 'comprehensive', name: '综合评估师', avatar: '📊', description: '综合评分和报告', enabled: true, priority: 6, timeout: 30, retries: 2 },
]

const users = [
  { id: 1, name: '张三', email: 'zhangsan@example.com', role: 'admin' },
  { id: 2, name: '李四', email: 'lisi@example.com', role: 'user' },
  { id: 3, name: '王五', email: 'wangwu@example.com', role: 'user' },
]

const getTabTitle = () => {
  const tab = tabs.find(t => t.id === activeTab.value)
  return tab?.name || ''
}
</script>
