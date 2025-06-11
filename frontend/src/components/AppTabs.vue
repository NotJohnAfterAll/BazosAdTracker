<template>  <nav class="border-b border-border mb-6">
    <ul class="flex space-x-8">
      <li>
        <button 
          :class="['tab', { 'data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm': activeTab === 'recent' }]"
          :data-state="activeTab === 'recent' ? 'active' : 'inactive'"
          @click="$emit('tab-change', 'recent')"
        >
          Recent Ads
        </button>
      </li>
      <li>
        <button 
          :class="['tab', { 'data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm': activeTab === 'keywords' }]"
          :data-state="activeTab === 'keywords' ? 'active' : 'inactive'"
          @click="$emit('tab-change', 'keywords')"
        >
          By Keywords
        </button>
      </li>
      <li>
        <button 
          :class="['tab', { 'data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm': activeTab === 'favorites' }]"
          :data-state="activeTab === 'favorites' ? 'active' : 'inactive'"
          @click="$emit('tab-change', 'favorites')"
        >
          <i class="fas fa-star text-yellow-500 mr-2"></i>Favorites
        </button>
      </li>
      <li>
        <button 
          :class="['tab', { 'data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm': activeTab === 'changes' }]"
          :data-state="activeTab === 'changes' ? 'active' : 'inactive'"
          @click="$emit('tab-change', 'changes')"
        >
          Changes Log
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
