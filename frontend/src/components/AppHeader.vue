<template>
  <header class="mb-8">
    <!-- Mobile layout -->
    <div class="md:hidden">
      <!-- Title and buttons row -->
      <div class="flex justify-between items-center mb-4">
        <h1 class="text-xl font-bold truncate mr-2 mobile-title">Bazos.cz Ad Tracker</h1>
        <div class="flex items-center space-x-2 flex-shrink-0">
          <!-- Settings button -->
          <Button variant="secondary" size="sm" @click="$emit('settings')" class="px-3 py-2 min-w-[44px] min-h-[44px]">
            <i class="fas fa-cog text-base"></i>
            <span class="sr-only">Settings</span>
          </Button>
          <!-- Manual check button -->
          <Button :disabled="loading" size="sm" @click="$emit('manual-check')" class="px-3 py-2 min-w-[44px] min-h-[44px]">
            <i :class="loading ? 'fas fa-spinner fa-spin text-base' : 'fas fa-sync text-base'"></i>
            <span class="sr-only">{{ loading ? 'Checking...' : 'Check Now' }}</span>
          </Button>
          <!-- Theme toggle -->
          <Button variant="secondary" size="sm" @click="$emit('theme-toggle')" class="px-3 py-2 min-w-[44px] min-h-[44px]">
            <i class="fas fa-moon text-base"></i>
            <span class="sr-only">Theme</span>
          </Button>
        </div>
      </div>
      
      <!-- Stats row -->
      <div class="text-xs text-muted-foreground bg-muted/50 rounded-lg p-2">
        <div class="grid grid-cols-3 gap-1 text-center">
          <div>
            <div class="font-semibold text-foreground text-sm">{{ stats.total_checks }}</div>
            <div class="text-xs">Checks</div>
          </div>
          <div>
            <div class="font-semibold text-foreground text-sm">{{ stats.total_ads }}</div>
            <div class="text-xs">Ads</div>
          </div>
          <div>
            <div class="font-semibold text-foreground text-sm">{{ stats.uptime }}</div>
            <div class="text-xs">Uptime</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Desktop layout -->
    <div class="hidden md:flex justify-between items-center mb-6">
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
