<template>
  <Card class="p-4 mb-6">
    <div class="space-y-4">
      <!-- Add keyword section - full width -->
      <div>
        <label for="new-keyword" class="block text-sm font-medium text-foreground mb-1">Add New Keyword</label>
        <div class="flex gap-2">
          <Input
            id="new-keyword"
            v-model="newKeyword"
            placeholder="Enter keyword to track"
            @keyup.enter="handleAddKeyword"
            class="flex-1"
          />
          <Button @click="handleAddKeyword" class="whitespace-nowrap" :disabled="loading">
            <i :class="loading ? 'fas fa-spinner fa-spin mr-2' : 'fas fa-plus mr-2'"></i> 
            {{ loading ? 'Adding...' : 'Add' }}
          </Button>
        </div>
      </div>
      
      <!-- Active keywords section -->
      <div>
        <label class="block text-sm font-medium text-foreground mb-1">Active Keywords</label>
        <div class="flex flex-wrap gap-2 min-h-[40px]">          <div
            v-for="keyword in keywords"
            :key="keyword"
            class="inline-flex items-center px-3 py-1 rounded-md text-sm bg-primary text-primary-foreground"
          >
            <span>{{ keyword }}</span>
            <button
              @click="$emit('remove-keyword', keyword)"
              :disabled="removeLoading === keyword"
              class="ml-2 hover:text-primary-foreground/80 disabled:opacity-50"
              :title="removeLoading === keyword ? 'Removing...' : 'Remove keyword'"
            >
              <i :class="removeLoading === keyword ? 'fas fa-spinner fa-spin text-xs' : 'fas fa-times text-xs'"></i>
            </button>
          </div>
          
          <div v-if="keywords.length === 0" class="text-sm text-muted-foreground">
            No keywords added yet
          </div>
        </div>
      </div>
    </div>
  </Card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Card from './ui/Card.vue'
import Input from './ui/Input.vue'
import Button from './ui/Button.vue'

interface Props {
  keywords: string[]
  loading?: boolean
  removeLoading?: string // keyword currently being removed
}

defineProps<Props>()

const emit = defineEmits<{
  'add-keyword': [keyword: string]
  'remove-keyword': [keyword: string]
}>()

const newKeyword = ref('')

const handleAddKeyword = () => {
  console.log('🔥 KeywordManager: handleAddKeyword called')
  console.log('🔥 KeywordManager: newKeyword.value =', `"${newKeyword.value}"`)
  console.log('🔥 KeywordManager: newKeyword.value.trim() =', `"${newKeyword.value.trim()}"`)
  console.log('🔥 KeywordManager: newKeyword.value.length =', newKeyword.value.length)
  
  if (newKeyword.value.trim()) {
    console.log('🔥 KeywordManager: Emitting add-keyword event with:', newKeyword.value.trim())
    emit('add-keyword', newKeyword.value.trim())
    newKeyword.value = ''
    console.log('🔥 KeywordManager: Event emitted and input cleared')
  } else {
    console.log('❌ KeywordManager: Empty keyword, not emitting')
    alert('⚠️ The keyword input appears to be empty. Please check if you typed something.')
  }
}
</script>
