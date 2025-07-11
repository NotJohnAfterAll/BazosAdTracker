<template>
  <div class="min-h-screen bg-background flex flex-col">
    <!-- Header with theme toggle -->
    <header class="w-full p-4 flex justify-between items-center border-b border-border">
      <h1 class="text-xl font-bold text-foreground">Bazos.cz Ad Tracker</h1>
      <Button variant="ghost" size="icon" @click="toggleTheme" class="ml-auto">
        <i :class="isDark ? 'fas fa-sun' : 'fas fa-moon'"></i>
        <span class="sr-only">Toggle theme</span>
      </Button>
    </header>

    <!-- Main content -->
    <div class="flex-1 flex items-center justify-center p-4">
      <Card class="w-full max-w-md">
        <div class="p-6 space-y-6">
          <!-- Title -->
          <div class="text-center space-y-2">
            <h2 class="text-2xl font-bold text-foreground">Sign in to your account</h2>
            <p class="text-sm text-muted-foreground">
              Or
              <router-link 
                to="/register" 
                class="font-medium text-primary hover:text-primary/80 underline-offset-4 hover:underline"
              >
                create a new account
              </router-link>
            </p>
          </div>

          <!-- Login form -->
          <form @submit.prevent="handleLogin" class="space-y-4">
            <!-- Username field -->
            <div class="space-y-2">
              <label for="username" class="text-sm font-medium text-foreground">
                Username or Email
              </label>
              <Input
                id="username"
                v-model="form.username"
                type="text"
                required
                placeholder="Enter your username or email"
                :disabled="loading"
              />
            </div>

            <!-- Password field -->
            <div class="space-y-2">
              <label for="password" class="text-sm font-medium text-foreground">
                Password
              </label>
              <Input
                id="password"
                v-model="form.password"
                type="password"
                required
                placeholder="Enter your password"
                :disabled="loading"
              />
            </div>

            <!-- Remember me -->
            <div class="flex items-center space-x-2">
              <input
                id="remember_me"
                v-model="form.remember_me"
                type="checkbox"
                class="h-4 w-4 rounded border-border text-primary focus:ring-primary focus:ring-offset-2 focus:ring-offset-background"
                :disabled="loading"
              />
              <label for="remember_me" class="text-sm text-muted-foreground">
                Remember me
              </label>
            </div>

            <!-- Error message -->
            <div v-if="error" class="p-3 rounded-md bg-destructive/15 border border-destructive/20">
              <p class="text-sm text-destructive">{{ error }}</p>
            </div>

            <!-- Submit button -->
            <Button
              type="submit"
              :disabled="loading"
              class="w-full"
            >
              <i v-if="loading" class="fas fa-spinner fa-spin mr-2"></i>
              <i v-else class="fas fa-sign-in-alt mr-2"></i>
              {{ loading ? 'Signing in...' : 'Sign in' }}
            </Button>
          </form>

          <!-- Additional links -->
          <div class="text-center">
            <p class="text-xs text-muted-foreground">
              By signing in, you agree to our terms of service and privacy policy.
            </p>
          </div>
        </div>
      </Card>
    </div>

    <!-- Footer -->
    <footer class="p-4 text-center border-t border-border">
      <p class="text-xs text-muted-foreground">
        © 2025 Bazos.cz Ad Tracker. Built with Vue.js and Tailwind CSS.
      </p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Button from '../components/ui/Button.vue'
import Input from '../components/ui/Input.vue'
import Card from '../components/ui/Card.vue'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const error = ref('')
const isDark = ref(false)

const form = reactive({
  username: '',
  password: '',
  remember_me: false
})

// Theme management
const toggleTheme = () => {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

// Initialize theme on mount
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  isDark.value = savedTheme === 'dark' || 
    (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)
  
  if (isDark.value) {
    document.documentElement.classList.add('dark')
  }
})

const handleLogin = async () => {
  loading.value = true
  error.value = ''

  try {
    const success = await authStore.login(form.username, form.password, form.remember_me)
    
    if (success) {
      router.push('/dashboard')
    } else {
      error.value = authStore.error || 'Login failed'
    }
  } catch (err) {
    error.value = 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
