<template>
  <div class="min-h-screen bg-background">
    <!-- Router View for different pages -->
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

// Initialize theme on app start
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    document.documentElement.classList.add('dark')
  }
})
</script>

<style scoped>
/* Global styles if needed */
</style>
