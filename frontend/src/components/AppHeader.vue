<template>
  <header class="mb-8">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">Bazos.cz Ad Tracker</h1>      <div class="flex items-center space-x-3">        <div class="text-xs text-muted-foreground">          <div class="flex space-x-4">
            <div>
              <span>Total checks: </span>
              <span class="font-semibold">{{ stats.total_checks }}</span>
            </div>
            <div>
              <span>Total ads: </span>
              <span class="font-semibold">{{ stats.total_ads }}</span>
            </div><div>
              <span>Uptime: </span>
              <span class="font-semibold">{{ stats.uptime }}</span>
            </div>
          </div>
        </div>
        
        <!-- Settings button -->
        <Button variant="secondary" @click="$emit('settings')">
          <i class="fas fa-cog mr-2"></i>
          <span>Settings</span>
        </Button>
          <!-- Manual check button -->
        <Button :disabled="loading" @click="$emit('manual-check')">
          <i :class="loading ? 'fas fa-spinner fa-spin mr-2' : 'fas fa-sync mr-2'"></i>
          <span>{{ loading ? 'Checking...' : 'Check Now' }}</span>
        </Button>
        
        <!-- Theme toggle -->
        <Button variant="secondary" @click="$emit('theme-toggle')">
          <i class="fas fa-moon mr-2"></i>
          <span>Theme</span>
        </Button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import Button from './ui/Button.vue'

interface Stats {
  total_checks: number
  total_ads: number
  uptime: string
  avg_duration: number
}

interface Props {
  stats: Stats
  loading?: boolean
}

defineProps<Props>()
defineEmits<{
  settings: []
  'manual-check': []
  'theme-toggle': []
}>()
</script>
