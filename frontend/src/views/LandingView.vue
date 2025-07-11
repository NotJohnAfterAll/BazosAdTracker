<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
    <!-- Navigation Bar -->
    <nav class="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <i class="fas fa-search text-white text-sm"></i>
            </div>
            <h1 class="text-xl font-bold text-gray-900 dark:text-white">Bazos Ad Tracker</h1>
          </div>
          
          <div class="flex items-center space-x-4">
            <Button variant="ghost" @click="toggleTheme" class="w-10 h-10 p-0">
              <i :class="isDarkMode ? 'fas fa-sun' : 'fas fa-moon'" class="text-gray-600 dark:text-gray-300"></i>
            </Button>
            <Button variant="outline" @click="$router.push('/login')" class="hidden sm:inline-flex" v-if="!isAuthenticated">
              Sign In
            </Button>
            <Button @click="$router.push('/register')" class="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700" v-if="!isAuthenticated">
              Get Started
            </Button>
            <Button @click="$router.push('/dashboard')" class="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700" v-if="isAuthenticated">
              Go to Dashboard
            </Button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="relative py-20 lg:py-32 overflow-hidden">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid lg:grid-cols-2 gap-12 items-center">
          <!-- Left Column - Content -->
          <div class="space-y-8">
            <div class="space-y-4">
              <div class="inline-flex items-center px-3 py-1 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 text-sm font-medium">
                <i class="fas fa-bell mr-2"></i>
                Real-time Notifications
              </div>
              <h1 class="text-4xl lg:text-6xl font-bold text-gray-900 dark:text-white leading-tight" v-if="!isAuthenticated">
                Never Miss a
                <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-purple-600">
                  Great Deal
                </span>
                on Bazos.cz
              </h1>
              <h1 class="text-4xl lg:text-6xl font-bold text-gray-900 dark:text-white leading-tight" v-else>
                Welcome Back!
                <span class="text-transparent bg-clip-text bg-gradient-to-r from-green-500 to-blue-600">
                  Continue Tracking
                </span>
                Your Deals
              </h1>
              <p class="text-xl text-gray-600 dark:text-gray-300 leading-relaxed" v-if="!isAuthenticated">
                Track classified ads automatically and get instant notifications when new items matching your interests are posted. Stay ahead of the competition.
              </p>
              <p class="text-xl text-gray-600 dark:text-gray-300 leading-relaxed" v-else>
                You're already set up and tracking deals! Visit your dashboard to manage keywords and view recent ads.
              </p>
            </div>

            <div class="flex flex-col sm:flex-row gap-4">
              <Button 
                @click="$router.push('/register')" 
                size="lg"
                class="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 px-8 py-4 text-lg"
                v-if="!isAuthenticated"
              >
                <i class="fas fa-rocket mr-2"></i>
                Start Tracking for Free
              </Button>
              <Button 
                @click="$router.push('/dashboard')" 
                size="lg"
                class="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 px-8 py-4 text-lg"
                v-if="isAuthenticated"
              >
                <i class="fas fa-tachometer-alt mr-2"></i>
                Go to Dashboard
              </Button>
              <Button 
                variant="outline" 
                size="lg"
                @click="scrollToFeatures"
                class="px-8 py-4 text-lg border-gray-300 dark:border-gray-600"
              >
                <i class="fas fa-play mr-2"></i>
                See How It Works
              </Button>
            </div>

            <!-- Stats -->
            <div class="grid grid-cols-3 gap-8 pt-8 border-t border-gray-200 dark:border-gray-700">
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-900 dark:text-white">24/7</div>
                <div class="text-sm text-gray-600 dark:text-gray-400">Monitoring</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-900 dark:text-white">Instant</div>
                <div class="text-sm text-gray-600 dark:text-gray-400">Alerts</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-900 dark:text-white">Free</div>
                <div class="text-sm text-gray-600 dark:text-gray-400">To Start</div>
              </div>
            </div>
          </div>

          <!-- Right Column - Visual -->
          <div class="relative">
            <div class="relative bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900 rounded-2xl shadow-2xl p-8 border border-gray-200 dark:border-gray-700">
              <!-- Mock browser window -->
              <div class="flex items-center space-x-2 mb-6">
                <div class="w-3 h-3 bg-red-400 rounded-full"></div>
                <div class="w-3 h-3 bg-yellow-400 rounded-full"></div>
                <div class="w-3 h-3 bg-green-400 rounded-full"></div>
                <div class="flex-1 bg-gray-100 dark:bg-gray-700 rounded px-3 py-1 ml-4">
                  <span class="text-xs text-gray-500 dark:text-gray-400">bazos-tracker.app</span>
                </div>
              </div>

              <!-- Mock dashboard content -->
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <h3 class="font-semibold text-gray-900 dark:text-white">Recent Ads</h3>
                  <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                </div>
                
                <!-- Mock ad cards -->
                <div class="space-y-3">
                  <div class="flex items-center space-x-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                    <div class="w-12 h-12 bg-gradient-to-br from-blue-400 to-blue-500 rounded-lg"></div>
                    <div class="flex-1 min-w-0">
                      <div class="text-sm font-medium text-gray-900 dark:text-white">MacBook Pro 2021</div>
                      <div class="text-xs text-gray-500 dark:text-gray-400">45,000 Kč • 2 min ago</div>
                    </div>
                    <div class="bg-green-500 text-white text-xs px-2 py-1 rounded-full font-medium">NEW</div>
                  </div>
                  
                  <div class="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div class="w-12 h-12 bg-gradient-to-br from-gray-400 to-gray-500 rounded-lg"></div>
                    <div class="flex-1 min-w-0">
                      <div class="text-sm font-medium text-gray-900 dark:text-white">iPhone 13 Pro</div>
                      <div class="text-xs text-gray-500 dark:text-gray-400">28,000 Kč • 1 hour ago</div>
                    </div>
                  </div>
                  
                  <div class="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div class="w-12 h-12 bg-gradient-to-br from-gray-400 to-gray-500 rounded-lg"></div>
                    <div class="flex-1 min-w-0">
                      <div class="text-sm font-medium text-gray-900 dark:text-white">Gaming Monitor</div>
                      <div class="text-xs text-gray-500 dark:text-gray-400">8,500 Kč • 3 hours ago</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Floating notification -->
            <div class="absolute -top-4 -right-4 bg-green-500 text-white p-3 rounded-lg shadow-lg animate-bounce">
              <div class="flex items-center space-x-2">
                <i class="fas fa-bell text-sm"></i>
                <span class="text-sm font-medium">New ad found!</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-20 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Everything You Need to Track Deals
          </h2>
          <p class="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Our powerful features help you stay on top of the Bazos.cz marketplace
          </p>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <!-- Feature 1 -->
          <div class="text-center p-6">
            <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4">
              <i class="fas fa-search text-white text-2xl"></i>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">Smart Keyword Tracking</h3>
            <p class="text-gray-600 dark:text-gray-300">
              Add keywords and let our system automatically scan for new ads matching your interests.
            </p>
          </div>

          <!-- Feature 2 -->
          <div class="text-center p-6">
            <div class="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center mx-auto mb-4">
              <i class="fas fa-bell text-white text-2xl"></i>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">Instant Notifications</h3>
            <p class="text-gray-600 dark:text-gray-300">
              Get notified immediately when new ads are posted so you can be the first to respond.
            </p>
          </div>

          <!-- Feature 3 -->
          <div class="text-center p-6">
            <div class="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center mx-auto mb-4">
              <i class="fas fa-heart text-white text-2xl"></i>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">Favorites & Organization</h3>
            <p class="text-gray-600 dark:text-gray-300">
              Save interesting ads to favorites and organize your findings for easy access.
            </p>
          </div>

          <!-- Feature 4 -->
          <div class="text-center p-6">
            <div class="w-16 h-16 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl flex items-center justify-center mx-auto mb-4">
              <i class="fas fa-chart-line text-white text-2xl"></i>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">Analytics & Insights</h3>
            <p class="text-gray-600 dark:text-gray-300">
              Track your search history and get insights into market trends and pricing.
            </p>
          </div>

          <!-- Feature 5 -->
          <div class="text-center p-6">
            <div class="w-16 h-16 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center mx-auto mb-4">
              <i class="fas fa-clock text-white text-2xl"></i>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">24/7 Monitoring</h3>
            <p class="text-gray-600 dark:text-gray-300">
              Our system works around the clock, so you never miss a deal even while you sleep.
            </p>
          </div>

          <!-- Feature 6 -->
          <div class="text-center p-6">
            <div class="w-16 h-16 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl flex items-center justify-center mx-auto mb-4">
              <i class="fas fa-mobile-alt text-white text-2xl"></i>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">Mobile Friendly</h3>
            <p class="text-gray-600 dark:text-gray-300">
              Access your tracked ads from any device with our responsive web interface.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-20 bg-gradient-to-r from-blue-500 to-purple-600" v-if="!isAuthenticated">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="text-3xl lg:text-4xl font-bold text-white mb-4">
          Ready to Find Your Next Great Deal?
        </h2>
        <p class="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
          Join thousands of users who never miss out on great deals from Bazos.cz
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <Button 
            @click="$router.push('/register')" 
            size="lg"
            class="bg-white text-blue-600 hover:bg-gray-50 px-8 py-4 text-lg font-semibold"
          >
            <i class="fas fa-user-plus mr-2"></i>
            Create Free Account
          </Button>
          <Button 
            variant="outline" 
            size="lg"
            @click="$router.push('/login')"
            class="border-white text-white hover:bg-white hover:text-blue-600 px-8 py-4 text-lg"
          >
            <i class="fas fa-sign-in-alt mr-2"></i>
            Sign In
          </Button>
        </div>
      </div>
    </section>

    <!-- Already logged in CTA Section -->
    <section class="py-20 bg-gradient-to-r from-green-500 to-blue-600" v-if="isAuthenticated">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="text-3xl lg:text-4xl font-bold text-white mb-4">
          Ready to Continue Tracking?
        </h2>
        <p class="text-xl text-green-100 mb-8 max-w-2xl mx-auto">
          Access your personalized dashboard to manage keywords and view recent ads
        </p>
        <Button 
          @click="$router.push('/dashboard')" 
          size="lg"
          class="bg-white text-green-600 hover:bg-gray-50 px-8 py-4 text-lg font-semibold"
        >
          <i class="fas fa-tachometer-alt mr-2"></i>
          Go to Dashboard
        </Button>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-gray-300 py-12">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid md:grid-cols-4 gap-8">
          <div class="md:col-span-2">
            <div class="flex items-center space-x-3 mb-4">
              <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                <i class="fas fa-search text-white text-sm"></i>
              </div>
              <h3 class="text-xl font-bold text-white">Bazos Ad Tracker</h3>
            </div>
            <p class="text-gray-400 mb-4 max-w-md">
              The smart way to track classified ads on Bazos.cz. Never miss a great deal again with real-time notifications and intelligent tracking.
            </p>
          </div>
          
          <div>
            <h4 class="text-white font-semibold mb-4">Features</h4>
            <ul class="space-y-2 text-sm">
              <li><a href="#" class="hover:text-white transition-colors">Keyword Tracking</a></li>
              <li><a href="#" class="hover:text-white transition-colors">Real-time Alerts</a></li>
              <li><a href="#" class="hover:text-white transition-colors">Favorites</a></li>
              <li><a href="#" class="hover:text-white transition-colors">Analytics</a></li>
            </ul>
          </div>
          
          <div>
            <h4 class="text-white font-semibold mb-4">Support</h4>
            <ul class="space-y-2 text-sm">
              <li><a href="#" class="hover:text-white transition-colors">Help Center</a></li>
              <li><a href="#" class="hover:text-white transition-colors">Contact</a></li>
              <li><a href="#" class="hover:text-white transition-colors">Privacy Policy</a></li>
              <li><a href="#" class="hover:text-white transition-colors">Terms of Service</a></li>
            </ul>
          </div>
        </div>
        
        <div class="border-t border-gray-800 mt-8 pt-8 text-center text-sm text-gray-400">
          <p>&copy; 2025 Bazos Ad Tracker. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import Button from '../components/ui/Button.vue'

const authStore = useAuthStore()
const isDarkMode = ref(false)

// Computed to check if user is authenticated
const isAuthenticated = computed(() => authStore.isAuthenticated)

// Check authentication on mount
onMounted(() => {
  // Load user from storage if needed
  if (!authStore.isAuthenticated) {
    authStore.loadFromStorage()
  }
  
  // Load theme
  const savedTheme = localStorage.getItem('theme')
  isDarkMode.value = savedTheme === 'dark' || 
    (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)
  
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark')
  }
})

const toggleTheme = () => {
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

const scrollToFeatures = () => {
  document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })
}
</script>
