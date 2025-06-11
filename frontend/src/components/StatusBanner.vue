<template>  <div 
    v-if="message"
    :class="[
      'border-l-4 p-4 mb-4 rounded-md',
      type === 'success' ? 'bg-green-50 border-green-500 dark:bg-green-900/20 dark:border-green-400' : '',
      type === 'error' ? 'bg-red-50 border-red-500 dark:bg-red-900/20 dark:border-red-400' : '',
      type === 'info' ? 'bg-blue-50 border-blue-500 dark:bg-blue-900/20 dark:border-blue-400' : ''
    ]"
  >
    <div class="flex">
      <div class="flex-shrink-0">        <i 
          :class="[
            'fas',
            type === 'success' ? 'fa-check-circle text-green-500 dark:text-green-400' : '',
            type === 'error' ? 'fa-exclamation-circle text-red-500 dark:text-red-400' : '',
            type === 'info' ? 'fa-info-circle text-blue-500 dark:text-blue-400' : ''
          ]"
        ></i>
      </div>
      <div class="ml-3">        <p 
          :class="[
            'text-sm',
            type === 'success' ? 'text-green-700 dark:text-green-300' : '',
            type === 'error' ? 'text-red-700 dark:text-red-300' : '',
            type === 'info' ? 'text-blue-700 dark:text-blue-300' : ''
          ]"
        >
          {{ message }}
        </p>
      </div>
      <div class="ml-auto pl-3">        <button
          @click="$emit('close')"
          :class="[
            'text-sm hover:opacity-80',
            type === 'success' ? 'text-green-700 dark:text-green-300' : '',
            type === 'error' ? 'text-red-700 dark:text-red-300' : '',
            type === 'info' ? 'text-blue-700 dark:text-blue-300' : ''
          ]"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  message: string
  type: 'success' | 'error' | 'info'
}

defineProps<Props>()
defineEmits<{
  close: []
}>()
</script>
