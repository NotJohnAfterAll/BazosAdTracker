<template>
  <div class="min-h-screen bg-background">
    <!-- Notification sound -->
    <audio ref="notificationSound" preload="auto">
      <source src="/notification.mp3" type="audio/mpeg">
    </audio>

    <div class="container mx-auto px-4 py-8">      <AppHeader 
        :stats="stats"
        :loading="loadingManualCheck"
        @settings="settingsOpen = true"
        @manual-check="handleManualCheck"
        @theme-toggle="toggleTheme"
      />

      <KeywordManager 
        :keywords="keywords"
        @add-keyword="handleAddKeyword"
        @remove-keyword="handleRemoveKeyword"
      />      <AppTabs 
        :active-tab="activeTab"
        @tab-change="activeTab = $event"
      />

      <!-- Status indicator -->
      <StatusBanner 
        v-if="statusMessage"
        :message="statusMessage"
        :type="statusType"
        @close="statusMessage = ''"
      />

      <!-- Tab content -->
      <main>
        <!-- Recent Ads Tab -->
        <RecentAdsTab 
          v-if="activeTab === 'recent'"
          :ads="recentAds"
          :loading="loadingRecent"
          @favorite="handleFavorite"
        />

        <!-- Keywords Tab -->
        <KeywordsTab 
          v-if="activeTab === 'keywords'"
          :keywords="keywords"
          :keyword-ads="keywordAds"
          :loading="loadingKeywords"
          :current-keyword="selectedKeyword"
          @keyword-select="handleKeywordSelect"
          @favorite="handleFavorite"
        />

        <!-- Favorites Tab -->
        <FavoritesTab 
          v-if="activeTab === 'favorites'"
          :favorites="favoriteAds"
          @favorite="handleFavorite"
        />

        <!-- Changes Log Tab -->
        <ChangesTab 
          v-if="activeTab === 'changes'"
          :changes="changesLog"
          :filter="changesFilter"
          @filter-change="changesFilter = $event"
        />
      </main>
    </div>

    <!-- Settings modal -->
    <SettingsModal 
      v-if="settingsOpen"
      :stats="stats"
      :notifications-enabled="notificationsEnabled"
      :sound-enabled="soundEnabled"
      @close="settingsOpen = false"
      @toggle-notifications="handleToggleNotifications"
      @toggle-sound="handleToggleSound"
      @refresh-stats="fetchStats"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { io, Socket } from 'socket.io-client'
import AppHeader from './components/AppHeader.vue'
import KeywordManager from './components/KeywordManager.vue'
import AppTabs from './components/AppTabs.vue'
import StatusBanner from './components/StatusBanner.vue'
import RecentAdsTab from './components/RecentAdsTab.vue'
import KeywordsTab from './components/KeywordsTab.vue'
import FavoritesTab from './components/FavoritesTab.vue'
import ChangesTab from './components/ChangesTab.vue'
import SettingsModal from './components/SettingsModal.vue'

// Types
interface Ad {
  id: string
  title: string
  price: string
  description: string
  image: string
  link: string
  seller_name: string
  date_added: string
  scraped_at: number
  isNew?: boolean
}

interface KeywordAd {
  keyword: string
  ad: Ad
}

interface Stats {
  total_checks: number
  total_ads: number
  uptime: string
  avg_duration: number
}

interface Change {
  timestamp: string
  type: 'new' | 'deleted'
  keyword: string
  ad: Ad
}

// Reactive state
const socket = ref<Socket | null>(null)
const notificationSound = ref<HTMLAudioElement>()

// UI state
const activeTab = ref('recent')
const settingsOpen = ref(false)
const statusMessage = ref('')
const statusType = ref<'success' | 'error' | 'info'>('info')

// Data state
const keywords = ref<string[]>([])
const recentAds = ref<KeywordAd[]>([])
const keywordAds = ref<Ad[]>([])
const selectedKeyword = ref('')
const favoriteAds = ref<Ad[]>([])
const changesLog = ref<Change[]>([])
const changesFilter = ref<'all' | 'new' | 'deleted'>('all')
const stats = ref<Stats>({
  total_checks: 0,
  total_ads: 0,
  uptime: '0 minutes',
  avg_duration: 0
})

// Loading states
const loadingRecent = ref(true)
const loadingKeywords = ref(false)
const loadingManualCheck = ref(false)

// Settings
const notificationsEnabled = ref(localStorage.getItem('notificationsEnabled') !== 'false')
const soundEnabled = ref(localStorage.getItem('soundEnabled') !== 'false')
const isDarkMode = ref(localStorage.getItem('darkMode') === 'true')

// API Base URL
const API_BASE = import.meta.env.VITE_API_URL || '/api'

// Initialize theme
if (isDarkMode.value) {
  document.documentElement.classList.add('dark')
}

// Socket.IO setup
const initSocket = () => {
  // Use environment variable or detect from current location
  const socketUrl = import.meta.env.VITE_SOCKET_URL || (
    // In production, use same origin (works with reverse proxy)
    import.meta.env.PROD 
      ? window.location.origin
      : (window.location.protocol === 'https:' 
          ? 'https://localhost:5000' 
          : 'http://localhost:5000')
  )
  
  socket.value = io(socketUrl, {
    transports: ['websocket', 'polling'],
    // Enable secure connection for HTTPS
    secure: window.location.protocol === 'https:',
    // Allow self-signed certificates in development only
    rejectUnauthorized: import.meta.env.PROD
  })
  socket.value.on('connect', () => {
    showStatus('Connected to server', 'success')
    stopNotificationPolling() // Stop polling when socket connects
  })

  socket.value.on('disconnect', () => {
    showStatus('Disconnected from server', 'error')
    startNotificationPolling() // Start polling when socket disconnects
  })

  socket.value.on('ads_update', (data: any) => {
    handleAdsUpdate(data)
  })
}

// API functions
const fetchKeywords = async () => {
  try {
    const response = await fetch(`${API_BASE}/keywords`)
    const data = await response.json()
    keywords.value = data.keywords || []
  } catch (error) {
    showStatus('Error fetching keywords', 'error')
    console.error('Error fetching keywords:', error)
  }
}

const fetchRecentAds = async () => {
  try {
    loadingRecent.value = true
    const response = await fetch(`${API_BASE}/recent-ads`)
    const data = await response.json()
    recentAds.value = data.ads || []
  } catch (error) {
    showStatus('Error fetching recent ads', 'error')
    console.error('Error fetching recent ads:', error)
  } finally {
    loadingRecent.value = false
  }
}

const fetchKeywordAds = async (keyword: string) => {
  try {
    loadingKeywords.value = true
    const response = await fetch(`${API_BASE}/ads?keyword=${encodeURIComponent(keyword)}`)
    const data = await response.json()
    keywordAds.value = data.ads || []
  } catch (error) {
    showStatus('Error fetching keyword ads', 'error')
    console.error('Error fetching keyword ads:', error)
  } finally {
    loadingKeywords.value = false
  }
}

// Helper functions
const formatUptime = (seconds: number): string => {
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (days > 0) {
    return `${days}d ${hours}h ${minutes}m`
  } else if (hours > 0) {
    return `${hours}h ${minutes}m`
  } else {
    return `${minutes} minutes`
  }
}

const fetchStats = async () => {
  try {
    const response = await fetch(`${API_BASE}/stats`)
    const data = await response.json()
    
    // Transform the nested API response to match our frontend interface
    stats.value = {
      total_checks: data.checks?.total || 0,
      total_ads: data.ads?.total_found || 0,
      uptime: formatUptime(data.system?.uptime_seconds || 0),
      avg_duration: data.checks?.avg_duration_ms || 0
    }
  } catch (error) {
    console.error('Error fetching stats:', error)
  }
}

// Event handlers
const handleAddKeyword = async (keyword: string) => {
  try {
    const response = await fetch(`${API_BASE}/keywords`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ keyword })
    })
    
    const data = await response.json()
    
    if (data.success) {
      keywords.value = data.keywords
      showStatus(`Keyword "${keyword}" added successfully`, 'success')
    } else {
      showStatus(data.error || 'Failed to add keyword', 'error')
    }
  } catch (error) {
    showStatus('Error adding keyword', 'error')
    console.error('Error adding keyword:', error)
  }
}

const handleRemoveKeyword = async (keyword: string) => {
  try {
    const response = await fetch(`${API_BASE}/keywords/${encodeURIComponent(keyword)}`, {
      method: 'DELETE'
    })
    
    const data = await response.json()
    
    if (data.success) {
      keywords.value = data.keywords
      showStatus(`Keyword "${keyword}" removed successfully`, 'success')
      
      // Clear selected keyword if it was deleted
      if (selectedKeyword.value === keyword) {
        selectedKeyword.value = ''
        keywordAds.value = []
      }
    } else {
      showStatus(data.error || 'Failed to remove keyword', 'error')
    }
  } catch (error) {
    showStatus('Error removing keyword', 'error')
    console.error('Error removing keyword:', error)
  }
}

const handleKeywordSelect = (keyword: string) => {
  selectedKeyword.value = keyword
  if (keyword) {
    fetchKeywordAds(keyword)
  } else {
    keywordAds.value = []
  }
}

const handleManualCheck = async () => {
  try {
    loadingManualCheck.value = true
    showStatus('Manual check started...', 'info')
    const response = await fetch(`${API_BASE}/manual-check`)
    const data = await response.json()
    
    if (data.status === 'success') {
      showStatus('Manual check completed successfully', 'success')
      // Refresh data after successful check
      fetchRecentAds()
      fetchStats()
    } else {
      showStatus(data.message || 'Manual check failed', 'error')
    }
  } catch (error) {
    showStatus('Error during manual check', 'error')
    console.error('Error during manual check:', error)
  } finally {
    loadingManualCheck.value = false
  }
}

const handleFavorite = (ad: Ad) => {
  const index = favoriteAds.value.findIndex(fav => fav.id === ad.id)
  
  if (index >= 0) {
    favoriteAds.value.splice(index, 1)
  } else {
    favoriteAds.value.push(ad)
  }
  
  // Save to localStorage
  localStorage.setItem('favoriteAds', JSON.stringify(favoriteAds.value))
}

const handleToggleNotifications = async () => {
  if (!notificationsEnabled.value && 'Notification' in window) {
    const permission = await Notification.requestPermission()
    if (permission === 'granted') {
      notificationsEnabled.value = true
    }
  } else {
    notificationsEnabled.value = !notificationsEnabled.value
  }
  
  localStorage.setItem('notificationsEnabled', notificationsEnabled.value.toString())
}

const handleToggleSound = () => {
  soundEnabled.value = !soundEnabled.value
  localStorage.setItem('soundEnabled', soundEnabled.value.toString())
}

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
  localStorage.setItem('darkMode', isDarkMode.value.toString())
  
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

const showStatus = (message: string, type: 'success' | 'error' | 'info') => {
  statusMessage.value = message
  statusType.value = type
  
  setTimeout(() => {
    statusMessage.value = ''
  }, 5000)
}

const playNotification = () => {
  if (soundEnabled.value && notificationSound.value) {
    notificationSound.value.play().catch(console.error)
  }
}

// Load favorites from localStorage
const loadFavorites = () => {
  const saved = localStorage.getItem('favoriteAds')
  if (saved) {
    try {
      favoriteAds.value = JSON.parse(saved)
    } catch (error) {
      console.error('Error loading favorites:', error)
    }
  }
}

// Lifecycle
onMounted(() => {
  initSocket()
  fetchKeywords()
  fetchRecentAds()
  fetchStats()
  loadFavorites()
  
  // Start notification polling as fallback
  setTimeout(() => {
    // Start polling after 30 seconds if socket not connected or in production
    if (!socket.value?.connected) {
      startNotificationPolling()
    }
  }, 30000)
  
  // Request notification permission if needed
  if (notificationsEnabled.value && 'Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission()
  }
})

onUnmounted(() => {
  if (socket.value) {
    socket.value.disconnect()
  }
  stopNotificationPolling()
})

// Notification polling for production (when scheduler runs separately)
let notificationPollingInterval: number | null = null

const startNotificationPolling = () => {
  // Poll for notifications every 30 seconds in production
  if (notificationPollingInterval) return
  
  console.log('Starting notification polling...')
  notificationPollingInterval = setInterval(() => {
    pollForNotifications()
  }, 30000)
}

const stopNotificationPolling = () => {
  if (notificationPollingInterval) {
    clearInterval(notificationPollingInterval)
    notificationPollingInterval = null
    console.log('Stopped notification polling')
  }
}

const pollForNotifications = async () => {
  try {
    const response = await fetch(`${API_BASE}/notifications`)
    const data = await response.json()
    
    if (data.new_ads?.length > 0 || data.deleted_ads?.length > 0) {
      handleAdsUpdate(data)
    }
  } catch (error) {
    console.error('Error polling notifications:', error)
  }
}

const handleAdsUpdate = (data: any) => {
  if (data.new_ads && data.new_ads.length > 0) {
    playNotification()
    
    // Add to changes log
    data.new_ads.forEach((item: KeywordAd) => {
      changesLog.value.unshift({
        timestamp: data.timestamp || new Date().toLocaleString(),
        type: 'new',
        keyword: item.keyword,
        ad: item.ad
      })
    })

    // Show browser notification
    if (notificationsEnabled.value && 'Notification' in window) {
      const totalNew = data.new_ads.length
      new Notification(`${totalNew} new ad${totalNew > 1 ? 's' : ''} found!`, {
        body: `Check the app for new advertisements`,
        icon: '/favicon.png'
      })
    }

    showStatus(`${data.new_ads.length} new ads found!`, 'success')
  }

  if (data.deleted_ads && data.deleted_ads.length > 0) {
    // Add to changes log
    data.deleted_ads.forEach((item: KeywordAd) => {
      changesLog.value.unshift({
        timestamp: data.timestamp || new Date().toLocaleString(),
        type: 'deleted',
        keyword: item.keyword,
        ad: item.ad
      })
    })
  }

  // Refresh current data
  fetchRecentAds()
  fetchStats()
  if (selectedKeyword.value) {
    fetchKeywordAds(selectedKeyword.value)
  }
}
</script>
