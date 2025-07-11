<template>
  <div class="min-h-screen bg-background">
    <!-- Unified header with navigation -->
    <AppHeader 
      v-if="!initialLoading"
      :stats="stats"
      :loading="loadingManualCheck"
      :user="user"
      :is-dark="isDarkMode"
      @settings="settingsOpen = true"
      @manual-check="handleManualCheck"
      @theme-toggle="toggleTheme"
      @logout="handleLogout"
    />

    <!-- Main Content -->
    <div v-if="!initialLoading" class="container mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">

      <!-- User-specific keyword manager -->
      <KeywordManager 
        :keywords="keywords"
        :loading="loadingAddKeyword"
        :remove-loading="removingKeyword || undefined"
        @add-keyword="handleAddKeyword"
        @remove-keyword="handleRemoveKeyword"
      />

      <AppTabs 
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
          :current-keyword="selectedKeyword || ''"
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

    <!-- Loading state -->
    <div v-else class="min-h-screen flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
        <p class="text-muted-foreground">Loading...</p>
      </div>
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
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { io, Socket } from 'socket.io-client'
import AppHeader from '../components/AppHeader.vue'
import KeywordManager from '../components/KeywordManager.vue'
import AppTabs from '../components/AppTabs.vue'
import StatusBanner from '../components/StatusBanner.vue'
import RecentAdsTab from '../components/RecentAdsTab.vue'
import KeywordsTab from '../components/KeywordsTab.vue'
import FavoritesTab from '../components/FavoritesTab.vue'
import ChangesTab from '../components/ChangesTab.vue'
import SettingsModal from '../components/SettingsModal.vue'

interface Ad {
  id: string          // Bazos ad ID (string)
  db_id?: number      // Database ID (for backend operations)
  title: string
  price: string
  description: string
  image: string
  image_url?: string
  link: string
  seller_name: string
  date_added: string
  scraped_at: number
  isNew?: boolean
  keyword?: string    // Associated keyword
}

// Router and stores
const router = useRouter()
const authStore = useAuthStore()

// User data
const user = computed(() => authStore.user)

// Component state
const activeTab = ref('recent')
const settingsOpen = ref(false)
const statusMessage = ref('')
const statusType = ref<'success' | 'error' | 'info'>('info')
const selectedKeyword = ref<string | null>(null)
const changesFilter = ref<'all' | 'new' | 'deleted'>('all')

// Data state
const keywords = ref<string[]>([])
const recentAds = ref<Ad[]>([])
const keywordAds = ref<Ad[]>([])
const favoriteAds = ref<Ad[]>([])
const changesLog = ref<any[]>([])
const stats = ref<any>({})

// Loading states
const loadingRecent = ref(false)
const loadingKeywords = ref(false)
const loadingAddKeyword = ref(false)
const removingKeyword = ref<string | null>(null) // Track which keyword is being removed
const loadingManualCheck = ref(false)
const initialLoading = ref(true)

// Settings
const notificationsEnabled = ref(false)
const soundEnabled = ref(false)
const isDarkMode = ref(false)

// Socket connection
let socket: Socket | null = null

// Methods
const handleLogout = async () => {
  await authStore.logout()
  router.push('/')
}

const fetchKeywords = async () => {
  try {
    const response = await authStore.apiRequest('/api/user/keywords')
    const data = await response.json()
    
    if (data.success) {
      keywords.value = data.keywords
    }
  } catch (error) {
    console.error('Failed to fetch keywords:', error)
  }
}

const fetchRecentAds = async (cacheBust = false) => {
  loadingRecent.value = true
  try {
    const url = cacheBust ? 
      `/api/user/recent-ads?_t=${Date.now()}` : 
      '/api/user/recent-ads'
    
    const response = await authStore.apiRequest(url)
    const data = await response.json()
    
    if (data.success) {
      // Ensure we have an array and each ad has required properties
      recentAds.value = (data.ads || []).filter((ad: any) => ad && ad.id)
      if (cacheBust) {
        console.log(`📡 Fetched ${recentAds.value.length} recent ads with cache-busting`)
      }
    } else {
      console.error('Failed to fetch recent ads:', data.error)
      recentAds.value = []
    }
  } catch (error) {
    console.error('Failed to fetch recent ads:', error)
    recentAds.value = []
  } finally {
    loadingRecent.value = false
  }
}

const fetchStats = async () => {
  try {
    const response = await authStore.apiRequest('/api/user/stats')
    const data = await response.json()
    
    if (data.success) {
      stats.value = data.stats
    }
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

const handleAddKeyword = async (keyword: string) => {
  loadingAddKeyword.value = true
  try {
    const response = await authStore.apiRequest('/api/user/keywords', {
      method: 'POST',
      body: JSON.stringify({ keyword })
    })
    
    const data = await response.json()
    
    if (data.success) {
      keywords.value = data.keywords
      statusMessage.value = data.message
      statusType.value = 'success'
      
      // Refresh data
      await fetchRecentAds()
      await fetchStats()
    } else {
      statusMessage.value = data.error
      statusType.value = 'error'
    }
  } catch (error) {
    console.error('Failed to add keyword:', error)
    statusMessage.value = 'Failed to add keyword'
    statusType.value = 'error'
  } finally {
    loadingAddKeyword.value = false
  }
}

const handleRemoveKeyword = async (keyword: string) => {
  removingKeyword.value = keyword
  try {
    const response = await authStore.apiRequest(`/api/user/keywords/${encodeURIComponent(keyword)}`, {
      method: 'DELETE'
    })
    
    const data = await response.json()
    
    if (data.success) {
      keywords.value = data.keywords
      statusMessage.value = data.message
      statusType.value = 'success'
      
      // If the removed keyword was currently selected, clear the selection and keyword ads
      if (selectedKeyword.value === keyword) {
        selectedKeyword.value = null
        keywordAds.value = []
      }
      
      // Force clear all ads arrays to prevent stale data
      console.log('🗑️ Clearing ads arrays before refresh...')
      recentAds.value = []
      favoriteAds.value = []
      
      // Small delay to ensure backend has processed the deletion
      await new Promise(resolve => setTimeout(resolve, 100))
      
      // Refresh all data with cache-busting
      console.log('🔄 Refreshing data after keyword removal...')
      const timestamp = Date.now()
      
      // Fetch recent ads with cache-busting
      const recentResponse = await authStore.apiRequest(`/api/user/recent-ads?_t=${timestamp}`)
      const recentData = await recentResponse.json()
      if (recentData.success) {
        // Filter ads and ensure no ads from removed keywords are shown
        const filteredAds = (recentData.ads || []).filter((ad: any) => {
          if (!ad || !ad.id) return false
          // Additional safety: check if the ad's keyword is still in our active keywords
          if (ad.keyword && !keywords.value.includes(ad.keyword)) {
            console.log(`🚫 Filtering out ad "${ad.title}" for removed keyword: ${ad.keyword}`)
            return false
          }
          return true
        })
        recentAds.value = filteredAds
      }
      console.log(`✅ Recent ads refreshed: ${recentAds.value.length} ads`)
      
      // Fetch favorites with cache-busting
      const favResponse = await authStore.apiRequest(`/api/user/favorites?_t=${timestamp}`)
      const favData = await favResponse.json()
      if (favData.success) {
        favoriteAds.value = favData.favorites || []
      }
      console.log(`✅ Favorites refreshed: ${favoriteAds.value.length} favorites`)
      
      // Refresh stats
      await fetchStats()
      
      // Force a complete re-render by clearing and re-fetching if user switches back to keywords tab
      if (activeTab.value === 'keywords' && selectedKeyword.value) {
        await handleKeywordSelect(selectedKeyword.value)
      }
    } else {
      statusMessage.value = data.error
      statusType.value = 'error'
    }
  } catch (error) {
    console.error('Failed to remove keyword:', error)
    statusMessage.value = 'Failed to remove keyword'
    statusType.value = 'error'
  } finally {
    removingKeyword.value = null
  }
}

const handleFavorite = async (ad: Ad) => {
  try {
    const response = await authStore.apiRequest('/api/user/favorites', {
      method: 'POST',
      body: JSON.stringify({ ad_id: ad.id })
    })
    
    const data = await response.json()
    
    if (data.success) {
      statusMessage.value = data.message
      statusType.value = 'success'
      
      // Refresh favorites if on favorites tab
      if (activeTab.value === 'favorites') {
        await fetchFavorites()
      }
    } else {
      statusMessage.value = data.error
      statusType.value = 'error'
    }
  } catch (error) {
    console.error('Failed to toggle favorite:', error)
    statusMessage.value = 'Failed to update favorites'
    statusType.value = 'error'
  }
}

const fetchFavorites = async () => {
  try {
    const response = await authStore.apiRequest('/api/user/favorites')
    const data = await response.json()
    
    if (data.success) {
      favoriteAds.value = data.favorites
    }
  } catch (error) {
    console.error('Failed to fetch favorites:', error)
  }
}

const handleKeywordSelect = async (keyword: string) => {
  selectedKeyword.value = keyword
  loadingKeywords.value = true
  
  try {
    const response = await authStore.apiRequest(`/api/user/ads?keyword=${encodeURIComponent(keyword)}`)
    const data = await response.json()
    
    if (data.success) {
      keywordAds.value = data.ads
    }
  } catch (error) {
    console.error('Failed to fetch keyword ads:', error)
  } finally {
    loadingKeywords.value = false
  }
}

const handleManualCheck = async () => {
  loadingManualCheck.value = true
  
  try {
    const response = await authStore.apiRequest('/api/user/manual-check')
    const data = await response.json()
    
    if (data.success) {
      statusMessage.value = `Manual check completed. Found ${data.new_ads} new ads, ${data.deleted_ads} removed.`
      statusType.value = 'success'
      
      // Play notification sound if new ads found and sound is enabled
      if (data.new_ads > 0 && soundEnabled.value) {
        console.log('🔊 Playing sound alert for new ads found')
        const audio = new Audio('/notification.mp3')
        audio.play().catch(console.error)
      }
      
      // If new ads were found, add a small delay to ensure database transaction is fully committed
      if (data.new_ads > 0) {
        console.log('⏳ Waiting for database to fully commit new ads...')
        await new Promise(resolve => setTimeout(resolve, 500))
      }
      
      // Refresh data sequentially to avoid race conditions
      console.log('🔄 Refreshing data after manual check...')
      await fetchRecentAds(true) // Use cache-busting
      await fetchStats()
      
      // If we're on favorites tab, refresh favorites too
      if (activeTab.value === 'favorites') {
        await fetchFavorites()
      }
      
      // If we're on keywords tab and have a selected keyword, refresh keyword ads
      if (activeTab.value === 'keywords' && selectedKeyword.value) {
        await handleKeywordSelect(selectedKeyword.value)
      }
      
      console.log('✅ Manual check and data refresh completed')
    } else {
      statusMessage.value = data.error
      statusType.value = 'error'
    }
  } catch (error) {
    console.error('Manual check failed:', error)
    statusMessage.value = 'Manual check failed'
    statusType.value = 'error'
  } finally {
    loadingManualCheck.value = false
  }
}

const handleToggleNotifications = () => {
  notificationsEnabled.value = !notificationsEnabled.value
  localStorage.setItem('notifications_enabled', notificationsEnabled.value.toString())
}

const handleToggleSound = () => {
  soundEnabled.value = !soundEnabled.value
  localStorage.setItem('sound_enabled', soundEnabled.value.toString())
}

const toggleTheme = () => {
  // Implement theme toggling
  const html = document.documentElement
  if (html.classList.contains('dark')) {
    html.classList.remove('dark')
    localStorage.setItem('theme', 'light')
    isDarkMode.value = false
  } else {
    html.classList.add('dark')
    localStorage.setItem('theme', 'dark')
    isDarkMode.value = true
  }
}

const initSocket = () => {
  if (!authStore.accessToken) {
    console.log('No access token, skipping socket connection')
    return
  }
  
  // Disconnect existing socket if any
  if (socket) {
    socket.disconnect()
  }
  
  console.log('Initializing socket connection...')
  socket = io('/', {
    auth: {
      token: authStore.accessToken
    },
    transports: ['polling'], // Start with polling for better compatibility
    autoConnect: true
  })
  
  socket.on('connect', () => {
    console.log('Socket connected successfully')
  })
  
  socket.on('connect_error', (error) => {
    console.error('Socket connection error:', error)
  })
  
  socket.on('ads_update', (data) => {
    console.log('Received ads update:', data)
    
    if (data.new_ads?.length > 0) {
      statusMessage.value = `Found ${data.new_ads.length} new ads!`
      statusType.value = 'success'
      
      // Play notification sound if enabled
      if (soundEnabled.value) {
        const audio = new Audio('/notification.mp3')
        audio.play().catch(console.error)
      }
    }
    
    // Refresh data
    fetchRecentAds()
    fetchStats()
  })
  
  socket.on('disconnect', (reason) => {
    console.log('Socket disconnected:', reason)
  })
}

// Lifecycle
onMounted(async () => {
  // Load settings from localStorage
  notificationsEnabled.value = localStorage.getItem('notifications_enabled') === 'true'
  soundEnabled.value = localStorage.getItem('sound_enabled') === 'true'
  
  // Load theme
  const savedTheme = localStorage.getItem('theme')
  isDarkMode.value = savedTheme === 'dark' || 
    (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)
  
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark')
  }
  
  try {
    // Initialize data
    await Promise.all([
      fetchKeywords(),
      fetchRecentAds(),
      fetchStats()
    ])
    
    // Initialize socket connection
    initSocket()
  } catch (error) {
    console.error('Error during initialization:', error)
  } finally {
    initialLoading.value = false
  }
})

onUnmounted(() => {
  if (socket) {
    socket.disconnect()
  }
})
</script>
