<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Create your account
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Or
          <router-link to="/login" class="font-medium text-indigo-600 hover:text-indigo-500">
            sign in to your existing account
          </router-link>
        </p>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="username" class="sr-only">Username</label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Username"
            />
          </div>
          <div>
            <label for="email" class="sr-only">Email</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Email address"
            />
          </div>
          <div>
            <label for="password" class="sr-only">Password</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Password"
            />
          </div>
          <div>
            <label for="confirmPassword" class="sr-only">Confirm Password</label>
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              type="password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Confirm Password"
            />
          </div>
        </div>

        <div class="text-sm text-gray-600">
          <p>Password requirements:</p>
          <ul class="list-disc list-inside mt-2 space-y-1">
            <li :class="{ 'text-green-600': passwordChecks.length, 'text-red-600': !passwordChecks.length }">
              At least 8 characters long
            </li>
            <li :class="{ 'text-green-600': passwordChecks.uppercase, 'text-red-600': !passwordChecks.uppercase }">
              Contains uppercase letter
            </li>
            <li :class="{ 'text-green-600': passwordChecks.lowercase, 'text-red-600': !passwordChecks.lowercase }">
              Contains lowercase letter
            </li>
            <li :class="{ 'text-green-600': passwordChecks.number, 'text-red-600': !passwordChecks.number }">
              Contains number
            </li>
          </ul>
        </div>

        <div v-if="error" class="rounded-md bg-red-50 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <i class="fas fa-exclamation-circle text-red-400" />
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">
                {{ error }}
              </h3>
            </div>
          </div>
        </div>

        <div v-if="success" class="rounded-md bg-green-50 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <i class="fas fa-check-circle text-green-400" />
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-green-800">
                Account created successfully! You can now sign in.
              </h3>
            </div>
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading || !isFormValid"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <i class="fas fa-spinner fa-spin text-indigo-500 group-hover:text-indigo-400" />
            </span>
            {{ loading ? 'Creating account...' : 'Create account' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const loading = ref(false)
const error = ref('')
const success = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const passwordChecks = computed(() => ({
  length: form.password.length >= 8,
  uppercase: /[A-Z]/.test(form.password),
  lowercase: /[a-z]/.test(form.password),
  number: /\d/.test(form.password)
}))

const isFormValid = computed(() => {
  return form.username.length >= 3 &&
         form.email.includes('@') &&
         passwordChecks.value.length &&
         passwordChecks.value.uppercase &&
         passwordChecks.value.lowercase &&
         passwordChecks.value.number &&
         form.password === form.confirmPassword
})

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  success.value = false

  if (form.password !== form.confirmPassword) {
    error.value = 'Passwords do not match'
    loading.value = false
    return
  }

  try {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: form.username,
        email: form.email,
        password: form.password
      })
    })

    const data = await response.json()

    if (data.success) {
      success.value = true
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    } else {
      error.value = data.error || 'Registration failed'
    }
  } catch (err) {
    error.value = 'Registration failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
