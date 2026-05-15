<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-2xl font-bold text-gray-800">知识库</h2>
        <p class="text-gray-500 mt-1">查阅法规标准和典型案例</p>
      </div>
      <div class="relative">
        <input 
          type="text" 
          placeholder="搜索知识库..." 
          class="w-80 pl-10 pr-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-primary-500"
        />
        <svg class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
      </div>
    </div>
    
    <div class="flex gap-6">
      <div class="w-64 bg-white rounded-xl border border-gray-100 overflow-hidden">
        <div class="p-4 border-b border-gray-200">
          <h3 class="font-semibold text-gray-800">知识分类</h3>
        </div>
        <div class="p-2">
          <div v-for="category in categories" :key="category.id" class="px-3 py-2 rounded-lg cursor-pointer transition-colors" :class="activeCategory === category.id ? 'bg-primary-50 text-primary-600' : 'hover:bg-gray-50 text-gray-600'">
            <div class="flex items-center justify-between">
              <span>{{ category.name }}</span>
              <span class="text-xs text-gray-400">{{ category.count }}</span>
            </div>
            <div v-if="category.children && activeCategory === category.id" class="mt-2 space-y-1">
              <div v-for="child in category.children" :key="child.id" class="pl-3 py-1 text-sm text-gray-500 hover:text-gray-700 cursor-pointer">
                {{ child.name }}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="flex-1 bg-white rounded-xl border border-gray-100 overflow-hidden">
        <div class="p-4 border-b border-gray-200">
          <h3 class="font-semibold text-gray-800">知识内容</h3>
        </div>
        <div class="p-6">
          <div class="bg-gray-50 rounded-xl p-6">
            <div class="flex items-start gap-4">
              <div class="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center shrink-0">
                <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                </svg>
              </div>
              <div class="flex-1">
                <h4 class="font-semibold text-gray-800 text-lg">中华人民共和国行政处罚法</h4>
                <p class="text-sm text-gray-500 mt-1">发布日期: 2021-01-22 | 修订日期: 2021-07-15</p>
                <p class="text-gray-600 mt-2">
                  《中华人民共和国行政处罚法》是为了规范行政处罚的设定和实施，保障和监督行政机关有效实施行政管理，维护公共利益和社会秩序，保护公民、法人或者其他组织的合法权益，根据宪法，制定的法律。
                </p>
              </div>
            </div>
            
            <div class="mt-6">
              <h5 class="font-medium text-gray-800 mb-3">相关条款</h5>
              <div class="space-y-3">
                <div v-for="article in articles" :key="article.id" class="bg-white rounded-lg p-4 border border-gray-100">
                  <div class="flex items-center gap-2 mb-2">
                    <span class="px-2 py-0.5 bg-primary-100 text-primary-700 rounded text-xs font-medium">{{ article.number }}</span>
                    <span class="font-medium text-gray-800">{{ article.title }}</span>
                  </div>
                  <p class="text-sm text-gray-600">{{ article.content }}</p>
                </div>
              </div>
            </div>
            
            <div class="flex items-center gap-3 mt-6">
              <button class="flex-1 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm">
                查看全文
              </button>
              <button class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm">
                收藏
              </button>
              <button class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm">
                引用
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeCategory = ref('laws')

const categories = [
  { id: 'laws', name: '法规标准', count: 45, children: [
    { id: 'law1', name: '法律' },
    { id: 'law2', name: '行政法规' },
    { id: 'law3', name: '部门规章' },
  ]},
  { id: 'cases', name: '典型案例', count: 128 },
  { id: 'materials', name: '学习资料', count: 67 },
  { id: 'faq', name: '常见问题', count: 34 },
]

const articles = [
  { id: 1, number: '第四条', title: '行政处罚遵循公正、公开的原则', content: '设定和实施行政处罚必须以事实为依据，与违法行为的事实、性质、情节以及社会危害程度相当。对违法行为给予行政处罚的规定必须公布；未经公布的，不得作为行政处罚的依据。' },
  { id: 2, number: '第四十四条', title: '告知程序', content: '行政机关在作出行政处罚决定之前，应当告知当事人拟作出的行政处罚内容及事实、理由、依据，并告知当事人依法享有的陈述、申辩、要求听证等权利。' },
  { id: 3, number: '第五十七条', title: '集体讨论', content: '对情节复杂或者重大违法行为给予行政处罚，行政机关负责人应当集体讨论决定。' },
]
</script>
