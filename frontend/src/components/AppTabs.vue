<template>  <nav class="border-b border-border mb-6">
    <ul class="flex space-x-2 sm:space-x-8 overflow-x-auto">
      <li class="flex-shrink-0">
        <button 
          :class="['tab', { 'data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm': activeTab === 'recent' }]"
          :data-state="activeTab === 'recent' ? 'active' : 'inactive'"
          @click="$emit('tab-change', 'recent')"
        >
          <span class="hidden sm:inline">Recent Ads</span>
          <span class="sm:hidden">Recent</span>
        </button>
      </li>
      <li class="flex-shrink-0">
        <button 
          :class="['tab', { 'data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm': activeTab === 'keywords' }]"
          :data-state="activeTab === 'keywords' ? 'active' : 'inactive'"
          @click="$emit('tab-change', 'keywords')"
        >
          <span class="hidden sm:inline">By Keywords</span>
          <span class="sm:hidden">Keywords</span>
        </button>
      </li>
      <li class="flex-shrink-0">
        <button 
          :class="['tab', { 'data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm': activeTab === 'favorites' }]"
          :data-state="activeTab === 'favorites' ? 'active' : 'inactive'"
          @click="$emit('tab-change', 'favorites')"
        >
          <i class="fas fa-star text-yellow-500 mr-1 sm:mr-2"></i>
          <span class="hidden sm:inline">Favorites</span>
          <span class="sm:hidden">Fav</span>
        </button>
      </li>
      <li class="flex-shrink-0">
        <button 
          :class="['tab', { 'data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm': activeTab === 'changes' }]"
          :data-state="activeTab === 'changes' ? 'active' : 'inactive'"
          @click="$emit('tab-change', 'changes')"
        >
          <span class="hidden sm:inline">Changes Log</span>
          <span class="sm:hidden">Changes</span>
        </button>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
interface Props {
  activeTab: string
}

defineProps<Props>()
defineEmits<{
  'tab-change': [tab: string]
}>()
</script>
