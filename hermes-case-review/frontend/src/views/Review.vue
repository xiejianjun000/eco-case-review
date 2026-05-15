<template>
  <div class="h-full flex">
    <div class="w-72 bg-white border-r border-gray-200 flex flex-col">
      <div class="p-4 border-b border-gray-200">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-gray-800">审查记录</h3>
          <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
          </button>
        </div>
        <div class="relative">
          <input 
            type="text" 
            placeholder="搜索案卷..." 
            class="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-primary-500 text-sm"
          />
          <svg class="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>
      </div>
      
      <div class="flex-1 overflow-auto">
        <div class="p-3">
          <div class="text-xs text-gray-500 mb-2 px-2">今日评查</div>
          <div 
            v-for="item in todayCases" 
            :key="item.id" 
            class="p-3 rounded-lg cursor-pointer transition-colors"
            :class="item.id === activeCase ? 'bg-primary-50 border border-primary-200' : 'hover:bg-gray-50'"
            @click="selectCase(item)"
          >
            <div class="font-medium text-gray-800 text-sm">{{ item.name }}</div>
            <div class="flex items-center justify-between mt-1">
              <span class="text-xs text-gray-500">{{ item.time }}</span>
              <span class="text-xs px-2 py-0.5 rounded-full" :class="item.status === 'completed' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'">
                {{ item.status === 'completed' ? '已完成' : '进行中' }}
              </span>
            </div>
          </div>
          
          <div class="text-xs text-gray-500 mb-2 px-2 mt-4">历史记录</div>
          <div 
            v-for="item in historyCases" 
            :key="item.id" 
            class="p-3 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
            @click="selectCase(item)"
          >
            <div class="font-medium text-gray-800 text-sm">{{ item.name }}</div>
            <div class="flex items-center justify-between mt-1">
              <span class="text-xs text-gray-500">{{ item.time }}</span>
              <span class="text-xs font-bold" :class="item.score >= 80 ? 'text-green-500' : item.score >= 60 ? 'text-yellow-500' : 'text-red-500'">{{ item.score }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="p-3 border-t border-gray-200">
        <div class="flex items-center gap-2">
          <div class="flex-1 bg-gray-100 rounded-lg p-2">
            <div class="text-xs text-gray-500">收藏夹</div>
            <div class="text-sm font-medium text-gray-800 mt-1">3个案卷</div>
          </div>
          <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
    
    <div class="flex-1 flex flex-col bg-gray-50">
      <div class="bg-white border-b border-gray-200 px-6 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-semibold text-gray-800">审查交流</h3>
            <p class="text-sm text-gray-500 mt-1">与智能体协作完成案卷评查</p>
          </div>
          <div class="flex items-center gap-3">
            <span class="px-3 py-1 text-sm bg-green-100 text-green-700 rounded-full flex items-center gap-1">
              <span class="w-2 h-2 bg-green-500 rounded-full"></span>
              6个智能体在线
            </span>
            <button class="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm">
              开始评查
            </button>
          </div>
        </div>
      </div>
      
      <div class="flex-1 overflow-auto p-6 space-y-4">
        <div 
          v-for="message in messages" 
          :key="message.id" 
          class="flex gap-3"
          :class="message.type === 'user' ? 'flex-row-reverse' : ''"
        >
          <div class="w-10 h-10 rounded-full flex items-center justify-center shrink-0" :class="message.type === 'user' ? 'bg-primary-500 text-white' : 'bg-gray-200 text-gray-600'">
            {{ message.type === 'user' ? '👤' : message.agentName?.charAt(0) }}
          </div>
          <div class="max-w-[70%]">
            <div class="flex items-center gap-2 mb-1">
              <span class="font-medium text-sm" :class="message.type === 'user' ? 'text-gray-600' : 'text-primary-600'">
                {{ message.type === 'user' ? '我' : message.agentName }}
              </span>
              <span class="text-xs text-gray-400">{{ formatTime(message.timestamp) }}</span>
            </div>
            <div 
              class="rounded-xl px-4 py-3"
              :class="message.type === 'user' ? 'bg-primary-500 text-white' : 'bg-white border border-gray-200'"
              v-html="renderMarkdown(message.content)"
            ></div>
            <div class="flex items-center gap-4 mt-2">
              <button class="flex items-center gap-1 text-xs hover:text-primary-500 transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path>
                </svg>
                👍
              </button>
              <button class="flex items-center gap-1 text-xs hover:text-red-500 transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"></path>
                </svg>
                👎
              </button>
              <button class="flex items-center gap-1 text-xs hover:text-gray-600 transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                </svg>
                复制
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="bg-white border-t border-gray-200 p-4">
        <div class="flex items-center gap-3 mb-3">
          <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"></path>
            </svg>
          </button>
          <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15.536a5 5 0 000-7.072m-2.828 9.9a9 9 0 000-12.728m19.5-3a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zm-17 0a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM12 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
          </button>
          <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </button>
          <div class="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg">
            <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
            </svg>
            <select class="bg-transparent border-none outline-none text-sm">
              <option>DeepSeek-V3</option>
              <option>GLM-4</option>
              <option>GPT-4o</option>
            </select>
          </div>
          <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
          </button>
        </div>
        
        <div class="relative">
          <textarea 
            v-model="inputMessage"
            placeholder="输入消息... 支持@智能体单独对话"
            class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:border-primary-500 resize-none"
            rows="2"
            @keydown.enter="sendMessage"
          ></textarea>
          <div class="absolute right-4 bottom-4 flex items-center gap-3">
            <button class="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors text-sm">
              暂停
            </button>
            <button class="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm">
              发送
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <div class="w-96 bg-white border-l border-gray-200 flex flex-col">
      <div class="flex items-center justify-between p-4 border-b border-gray-200">
        <h3 class="font-semibold text-gray-800">审查详情</h3>
        <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
          </svg>
        </button>
      </div>
      
      <div class="flex-1 overflow-auto">
        <div class="border-b border-gray-200">
          <div class="p-4 cursor-pointer hover:bg-gray-50 transition-colors" @click="activePanel = 'pdf'">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                </svg>
                <span class="font-medium text-gray-800">案卷预览</span>
              </div>
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </div>
          </div>
          <div v-if="activePanel === 'pdf'" class="p-4">
            <div class="bg-gray-100 rounded-lg h-64 flex items-center justify-center">
              <div class="text-center text-gray-500">
                <svg class="w-16 h-16 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                </svg>
                <div>案卷PDF预览区域</div>
                <div class="text-sm mt-1">第 3/23 页</div>
              </div>
            </div>
            <div class="flex items-center justify-between mt-3">
              <div class="flex items-center gap-2">
                <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                  <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                  </svg>
                </button>
                <span class="text-sm text-gray-600">第 3 页</span>
                <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                  <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                  </svg>
                </button>
              </div>
              <div class="flex items-center gap-2">
                <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                  <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="border-b border-gray-200">
          <div class="p-4 cursor-pointer hover:bg-gray-50 transition-colors" @click="activePanel = 'progress'">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
                <span class="font-medium text-gray-800">审查进度</span>
              </div>
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </div>
          </div>
          <div v-if="activePanel === 'progress'" class="p-4">
            <div class="space-y-3">
              <div v-for="(step, index) in reviewSteps" :key="index" class="flex items-start gap-3">
                <div 
                  class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
                  :class="getStepClass(step.status)"
                >
                  {{ step.status === 'completed' ? '✓' : step.status === 'running' ? '⚡' : index + 1 }}
                </div>
                <div class="flex-1">
                  <div class="flex items-center justify-between">
                    <span class="font-medium text-sm" :class="step.status === 'completed' ? 'text-green-600' : step.status === 'running' ? 'text-primary-600' : 'text-gray-600'">{{ step.name }}</span>
                    <span class="text-xs text-gray-400">{{ step.time }}</span>
                  </div>
                  <div v-if="step.status === 'running'" class="mt-1">
                    <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div class="h-full bg-primary-500 rounded-full progress-bar"></div>
                    </div>
                    <div class="text-xs text-gray-500 mt-1">{{ step.progress }}</div>
                  </div>
                  <div v-if="step.status === 'completed' && step.score !== undefined" class="text-xs text-green-500 mt-1">得分: {{ step.score }}</div>
                </div>
              </div>
            </div>
            
            <div class="flex items-center gap-3 mt-4">
              <button class="flex-1 px-4 py-2 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition-colors text-sm">
                ⏸️ 暂停
              </button>
              <button class="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm">
                ▶️ 继续
              </button>
            </div>
          </div>
        </div>
        
        <div class="border-b border-gray-200">
          <div class="p-4 cursor-pointer hover:bg-gray-50 transition-colors" @click="activePanel = 'report'">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                <span class="font-medium text-gray-800">评查报告</span>
              </div>
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </div>
          </div>
          <div v-if="activePanel === 'report'" class="p-4">
            <div class="bg-gray-50 rounded-lg p-4">
              <div class="text-center mb-4">
                <div class="text-4xl font-bold text-primary-500">89.5</div>
                <div class="text-sm text-gray-500 mt-1">综合得分</div>
                <div class="text-lg font-semibold text-green-600">优秀</div>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div class="bg-white rounded-lg p-3 text-center">
                  <div class="text-xl font-bold text-gray-800">50</div>
                  <div class="text-xs text-gray-500">合法性</div>
                </div>
                <div class="bg-white rounded-lg p-3 text-center">
                  <div class="text-xl font-bold text-gray-800">39.5</div>
                  <div class="text-xs text-gray-500">规范性</div>
                </div>
              </div>
              <div class="flex gap-2 mt-4">
                <button class="flex-1 px-3 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm flex items-center justify-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  PDF
                </button>
                <button class="flex-1 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm flex items-center justify-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16h-2v-6a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V16h-2v-3.586l-2.293 2.293M7 16h2.586l2-2H14M7 16h2c.266 0 .52-.097.707-.293l3-3c.187-.187.293-.441.293-.707V10c0-.552-.448-1-1-1H7c-.552 0-1 .448-1 1v6z"></path>
                  </svg>
                  Word
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="p-4">
          <div class="flex items-center gap-2 mb-3">
            <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
            </svg>
            <span class="font-medium text-gray-800">智能体状态</span>
          </div>
          <div class="space-y-2">
            <div v-for="agent in agentStatus" :key="agent.id" class="flex items-center justify-between p-2 rounded-lg" :class="agent.status === 'running' ? 'bg-green-50' : 'bg-gray-50'">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full" :class="agent.status === 'running' ? 'bg-green-500' : agent.status === 'waiting' ? 'bg-yellow-500' : 'bg-gray-300'"></span>
                <span class="text-sm text-gray-700">{{ agent.name }}</span>
              </div>
              <span class="text-xs px-2 py-0.5 rounded-full" :class="getStatusClass(agent.status)">{{ getStatusText(agent.status) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import markdownIt from 'markdown-it'

const md = markdownIt()

const inputMessage = ref('')
const activeCase = ref(1)
const activePanel = ref('pdf')

const todayCases = [
  { id: 1, name: '案卷2024-001', time: '10分钟前', status: 'completed' },
  { id: 2, name: '案卷2024-002', time: '25分钟前', status: 'reviewing' },
  { id: 3, name: '案卷2024-003', time: '1小时前', status: 'reviewing' },
]

const historyCases = [
  { id: 4, name: '案卷2024-089', time: '昨天', score: 76.5 },
  { id: 5, name: '案卷2024-088', time: '昨天', score: 92.3 },
  { id: 6, name: '案卷2024-087', time: '2天前', score: 58.0 },
]

const messages = reactive([
  { id: 1, type: 'agent', content: '您好！我是您的智能评查助手，请问需要我帮您审查哪个案卷？', agentName: '综合评估师', timestamp: new Date() },
  { id: 2, type: 'user', content: '请帮我审查案卷2024-001', agentName: undefined, timestamp: new Date() },
  { id: 3, type: 'agent', content: '好的，正在启动评查流程...\n\n**审查进度**\n\n1. ✅ 文件解析完成（23页PDF）\n2. ⚡ 合法性审查中（12/25项）\n3. ⏳ 等待中\n\n预计完成时间：约3分钟', agentName: '综合评估师', timestamp: new Date() },
])

const reviewSteps = [
  { name: '文件解析', status: 'completed', time: '0.5s', score: 100 },
  { name: '合法性审查', status: 'running', time: '12s', progress: '48%' },
  { name: '规范性审查', status: 'pending', time: '-', progress: '-' },
  { name: '裁量基准计算', status: 'pending', time: '-', progress: '-' },
  { name: '证据链分析', status: 'pending', time: '-', progress: '-' },
  { name: '综合报告生成', status: 'pending', time: '-', progress: '-' },
]

const agentStatus = [
  { id: 'legality', name: '合法性审查员', status: 'running' },
  { id: 'normative', name: '规范性审查员', status: 'waiting' },
  { id: 'discretion', name: '裁量计算师', status: 'waiting' },
  { id: 'evidence', name: '证据分析师', status: 'waiting' },
  { id: 'document', name: '文书审计员', status: 'running' },
  { id: 'comprehensive', name: '综合评估师', status: 'idle' },
]

const selectCase = (item: any) => {
  activeCase.value = item.id
}

const sendMessage = () => {
  if (!inputMessage.value.trim()) return
  
  messages.push({
    id: Date.now(),
    type: 'user',
    content: inputMessage.value,
    agentName: undefined,
    timestamp: new Date(),
  })
  
  inputMessage.value = ''
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const renderMarkdown = (content: string) => {
  return md.render(content)
}

const getStepClass = (status: string) => {
  if (status === 'completed') return 'bg-green-500 text-white'
  if (status === 'running') return 'bg-primary-500 text-white'
  return 'bg-gray-200 text-gray-600'
}

const getStatusClass = (status: string) => {
  if (status === 'running') return 'bg-green-100 text-green-700'
  if (status === 'waiting') return 'bg-yellow-100 text-yellow-700'
  return 'bg-gray-100 text-gray-600'
}

const getStatusText = (status: string) => {
  if (status === 'running') return '运行中'
  if (status === 'waiting') return '等待中'
  return '空闲'
}
</script>
