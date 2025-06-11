<template>
  <Dialog :open="true" @close="$emit('close')">
    <div class="p-4 border-b border-border">
      <div class="flex justify-between items-center">
        <h3 class="text-lg font-semibold">Settings</h3>
        <button @click="$emit('close')" class="text-muted-foreground hover:text-foreground">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>
    
    <div class="p-4">
      <div class="mb-4">
        <h4 class="text-md font-medium mb-2">Notifications</h4>
        
        <div class="flex justify-between items-center py-2 border-b border-border">
          <div>
            <p class="font-medium">Browser Notifications</p>
            <p class="text-sm text-muted-foreground">Show notifications when new ads are found</p>
          </div>
          <div class="flex items-center">
            <Button
              v-if="showNotificationPermissionBtn"
              variant="secondary"
              size="sm"
              class="mr-2"
              @click="requestNotificationPermission"
            >
              Enable
            </Button>
            <label class="switch">
              <input
                type="checkbox"
                :checked="notificationsEnabled"
                @change="$emit('toggle-notifications')"
              >
              <span class="slider"></span>
            </label>
          </div>
        </div>
        
        <div class="flex justify-between items-center py-2 border-b border-border">
          <div>
            <p class="font-medium">Sound Alerts</p>
            <p class="text-sm text-muted-foreground">Play sound when new ads are found</p>
          </div>
          <label class="switch">
            <input
              type="checkbox"
              :checked="soundEnabled"
              @change="$emit('toggle-sound')"
            >
            <span class="slider"></span>
          </label>
        </div>
      </div>
      
      <div class="mb-4">
        <h4 class="text-md font-medium mb-2">System Information</h4>
        <div class="bg-muted p-3 rounded">
          <div class="grid grid-cols-2 gap-y-2 text-sm">
            <div>Check Interval:</div>
            <div class="text-right font-medium">5 minutes</div>
            
            <div>Average Check Duration:</div>
            <div class="text-right font-medium">{{ stats.avg_duration }} ms</div>
            
            <div>Total Checks:</div>
            <div class="text-right font-medium">{{ stats.total_checks }}</div>
            
            <div>Total Ads Found:</div>
            <div class="text-right font-medium">{{ stats.total_ads }}</div>
            
            <div>System Uptime:</div>
            <div class="text-right font-medium">{{ stats.uptime }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="p-4 bg-muted rounded-b">
      <div class="flex justify-between">
        <Button variant="secondary" @click="$emit('refresh-stats')">
          <i class="fas fa-sync mr-2"></i>
          Refresh Stats
        </Button>
        <Button @click="$emit('close')">
          Close
        </Button>
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import Dialog from './ui/Dialog.vue'
import Button from './ui/Button.vue'

interface Stats {
  total_checks: number
  total_ads: number
  uptime: string
  avg_duration: number
}

interface Props {
  stats: Stats
  notificationsEnabled: boolean
  soundEnabled: boolean
}

defineProps<Props>()
defineEmits<{
  close: []
  'toggle-notifications': []
  'toggle-sound': []
  'refresh-stats': []
}>()

const showNotificationPermissionBtn = computed(() => {
  return 'Notification' in window && Notification.permission === 'default'
})

const requestNotificationPermission = async () => {
  if ('Notification' in window) {
    await Notification.requestPermission()
  }
}
</script>
