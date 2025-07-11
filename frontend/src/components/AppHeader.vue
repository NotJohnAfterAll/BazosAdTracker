<template>
  <!-- Unified Navigation Bar -->
  <nav class="bg-card shadow-sm border-b border-border">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- Left side - Logo/Title -->
        <div class="flex items-center">
          <router-link to="/" class="text-xl font-bold text-foreground hover:text-primary transition-colors cursor-pointer">
            Bazos.cz Ad Tracker
          </router-link>
        </div>
        
        <!-- Right side - User controls -->
        <div class="flex items-center space-x-3">
          <!-- Desktop: Stats display -->
          <div class="hidden lg:flex items-center space-x-6 text-xs text-muted-foreground mr-4">
            <div class="flex items-center space-x-1">
              <i class="fas fa-chart-line"></i>
              <span>{{ stats.total_checks }} checks</span>
            </div>
            <div class="flex items-center space-x-1">
              <i class="fas fa-ad"></i>
              <span>{{ stats.total_ads }} ads</span>
            </div>
            <div class="flex items-center space-x-1">
              <i class="fas fa-clock"></i>
              <span>{{ stats.uptime }}</span>
            </div>
          </div>

          <!-- Action buttons -->
          <div class="flex items-center space-x-2">
            <!-- Settings button -->
            <Button variant="ghost" size="icon" @click="$emit('settings')" title="Settings">
              <i class="fas fa-cog"></i>
              <span class="sr-only">Settings</span>
            </Button>
            
            <!-- Manual check button -->
            <Button variant="ghost" size="icon" :disabled="loading" @click="$emit('manual-check')" title="Check for new ads now">
              <i :class="loading ? 'fas fa-spinner fa-spin' : 'fas fa-sync'"></i>
              <span class="sr-only">{{ loading ? 'Checking...' : 'Check Now' }}</span>
            </Button>
            
            <!-- Theme toggle -->
            <Button variant="ghost" size="icon" @click="$emit('theme-toggle')" title="Toggle dark/light theme">
              <i :class="isDark ? 'far fa-sun' : 'fas fa-moon'"></i>
              <span class="sr-only">Toggle theme</span>
            </Button>
          </div>

          <!-- User info (desktop only) -->
          <div v-if="user" class="hidden sm:flex items-center space-x-3">
            <div class="text-right">
              <div class="text-sm font-medium text-foreground">{{ user.username }}</div>
              <div class="text-xs text-muted-foreground">{{ user.email }}</div>
            </div>
            <div class="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
              <span class="text-sm font-medium text-primary-foreground">
                {{ user.username.charAt(0).toUpperCase() }}
              </span>
            </div>
          </div>

          <!-- Mobile user indicator -->
          <div v-if="user" class="sm:hidden w-8 h-8 bg-primary rounded-full flex items-center justify-center">
            <span class="text-sm font-medium text-primary-foreground">
              {{ user.username.charAt(0).toUpperCase() }}
            </span>
          </div>

          <!-- Logout button -->
          <Button variant="outline" size="sm" @click="$emit('logout')" title="Sign out">
            <i class="fas fa-sign-out-alt mr-2"></i>
            <span class="hidden sm:inline">Logout</span>
            <span class="sm:hidden sr-only">Logout</span>
          </Button>
        </div>
      </div>
    </div>

    <!-- Mobile stats bar -->
    <div class="md:hidden">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 pb-3">
        <div class="text-xs text-muted-foreground bg-muted/50 rounded-lg p-3">
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
    </div>
  </nav>
</template>

<script setup lang="ts">
import Button from './ui/Button.vue'

interface User {
  id: number
  username: string
  email: string
  is_active: boolean
  is_verified: boolean
  created_at: string
  last_login: string | null
  keywords_count: number
  ads_count: number
  favorites_count: number
}

interface Stats {
  total_checks: number
  total_ads: number
  uptime: string
  avg_duration: number
  check_interval_minutes?: number
  uptime_seconds?: number
  active_keywords?: number
  favorites_count?: number
  check_interval?: number
  last_check_at?: string
}

interface Props {
  stats: Stats
  loading?: boolean
  user?: User | null
  isDark?: boolean
}

defineProps<Props>()
defineEmits<{
  settings: []
  'manual-check': []
  'theme-toggle': []
  logout: []
}>()
</script>
