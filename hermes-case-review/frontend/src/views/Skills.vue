<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-2xl font-bold text-gray-800">技能广场</h2>
        <p class="text-gray-500 mt-1">发现和安装实用的评查技能</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="relative">
          <input 
            type="text" 
            placeholder="搜索技能..." 
            class="w-64 pl-10 pr-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-primary-500"
          />
          <svg class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>
        <select class="px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-primary-500">
          <option>全部分类</option>
          <option>审查技能</option>
          <option>分析工具</option>
          <option>报告生成</option>
          <option>数据处理</option>
        </select>
        <select class="px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-primary-500">
          <option>最新发布</option>
          <option>安装量</option>
          <option>评分</option>
        </select>
      </div>
    </div>
    
    <div class="grid grid-cols-3 gap-4">
      <div v-for="skill in skills" :key="skill.id" class="bg-white rounded-xl p-5 border border-gray-100 hover:shadow-lg transition-all">
        <div class="flex items-start justify-between mb-4">
          <div class="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center text-2xl">
            {{ skill.icon }}
          </div>
          <div class="flex items-center gap-1">
            <svg class="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path>
            </svg>
            <span class="text-sm font-medium text-gray-700">{{ skill.rating }}</span>
          </div>
        </div>
        
        <h3 class="font-semibold text-gray-800 text-lg">{{ skill.name }}</h3>
        <p class="text-sm text-gray-500 mt-2 line-clamp-2">{{ skill.description }}</p>
        
        <div class="flex items-center gap-4 mt-4 text-xs text-gray-500">
          <span class="flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
            </svg>
            {{ skill.author }}
          </span>
          <span class="flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
            </svg>
            {{ skill.downloads }} 安装
          </span>
        </div>
        
        <div class="flex items-center gap-2 mt-4 pt-4 border-t border-gray-100">
          <button class="flex-1 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm">
            {{ skill.installed ? '已安装' : '安装' }}
          </button>
          <button class="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm">
            详情
          </button>
        </div>
      </div>
    </div>
    
    <div class="mt-6 flex items-center justify-center gap-2">
      <button class="px-3 py-1 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">上一页</button>
      <button class="px-3 py-1 text-sm bg-primary-500 text-white rounded-lg">1</button>
      <button class="px-3 py-1 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">2</button>
      <button class="px-3 py-1 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">3</button>
      <button class="px-3 py-1 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">下一页</button>
    </div>
  </div>
</template>

<script setup lang="ts">
const skills = [
  { id: 1, name: '法规检索助手', icon: '📚', description: '快速检索生态环境相关法律法规，支持关键词搜索和条款定位', author: '官方', downloads: '1.2k', rating: '4.8', installed: true },
  { id: 2, name: '数据统计工具', icon: '📊', description: '统计分析评查数据，生成可视化报表和趋势分析', author: '官方', downloads: '890', rating: '4.5', installed: true },
  { id: 3, name: '文书生成器', icon: '📝', description: '根据评查结果自动生成规范的行政处罚决定书', author: '用户甲', downloads: '567', rating: '4.9', installed: false },
  { id: 4, name: '证据链分析', icon: '🔍', description: '分析证据链完整性，识别证据漏洞和改进建议', author: '官方', downloads: '432', rating: '4.7', installed: true },
  { id: 5, name: '裁量计算器', icon: '🧮', description: '根据裁量基准自动计算罚款金额，确保过罚相当', author: '官方', downloads: '389', rating: '4.6', installed: true },
  { id: 6, name: '案例对比工具', icon: '🔄', description: '对比分析同类案件，提供参考依据和改进方向', author: '用户乙', downloads: '256', rating: '4.4', installed: false },
]
</script>
