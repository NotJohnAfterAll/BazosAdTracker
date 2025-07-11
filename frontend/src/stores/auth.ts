/**
 * Authentication store for managing user state
 */
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export interface User {
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

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!user.value && !!accessToken.value)
  const isLoading = computed(() => loading.value)

  // Actions
  const login = async (username: string, password: string, rememberMe = false): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username,
          password,
          remember_me: rememberMe
        })
      })

      const data = await response.json()

      if (data.success) {
        user.value = data.user
        accessToken.value = data.access_token
        refreshToken.value = data.refresh_token
        
        // Store tokens in localStorage for persistence
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        localStorage.setItem('user', JSON.stringify(data.user))
        
        return true
      } else {
        error.value = data.error
        return false
      }
    } catch (err) {
      error.value = 'Login failed. Please try again.'
      return false
    } finally {
      loading.value = false
    }
  }

  const logout = async (): Promise<void> => {
    loading.value = true

    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken.value}`,
          'Content-Type': 'application/json'
        }
      })
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      // Clear state regardless of API response
      user.value = null
      accessToken.value = null
      refreshToken.value = null
      
      // Clear localStorage
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      
      loading.value = false
    }
  }

  const loadFromStorage = (): void => {
    const storedToken = localStorage.getItem('access_token')
    const storedRefreshToken = localStorage.getItem('refresh_token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      try {
        accessToken.value = storedToken
        refreshToken.value = storedRefreshToken
        user.value = JSON.parse(storedUser)
      } catch (err) {
        console.error('Failed to load user from storage:', err)
        localStorage.clear()
      }
    }
  }

  const getCurrentUser = async (): Promise<boolean> => {
    if (!accessToken.value) {
      return false
    }

    loading.value = true
    
    try {
      const response = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${accessToken.value}`
        }
      })

      const data = await response.json()

      if (data.success) {
        user.value = data.user
        localStorage.setItem('user', JSON.stringify(data.user))
        return true
      } else {
        // Token might be expired, clear auth state
        await logout()
        return false
      }
    } catch (err) {
      console.error('Get current user error:', err)
      await logout()
      return false
    } finally {
      loading.value = false
    }
  }

  const updateUser = (userData: Partial<User>): void => {
    if (user.value) {
      user.value = { ...user.value, ...userData }
      localStorage.setItem('user', JSON.stringify(user.value))
    }
  }

  const apiRequest = async (url: string, options: RequestInit = {}): Promise<Response> => {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    }

    if (accessToken.value) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${accessToken.value}`
    }

    const response = await fetch(url, {
      ...options,
      headers
    })

    // Handle token expiration
    if (response.status === 401 && accessToken.value) {
      await logout()
      window.location.href = '/login'
    }

    return response
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    loading,
    error,
    
    // Getters
    isAuthenticated,
    isLoading,
    
    // Actions
    login,
    logout,
    loadFromStorage,
    getCurrentUser,
    updateUser,
    apiRequest
  }
})
