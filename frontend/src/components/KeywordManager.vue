<template>
  <Card class="p-4 mb-6">
    <div class="flex flex-col md:flex-row gap-4 items-start md:items-center">
      <div class="flex-grow">
        <label for="new-keyword" class="block text-sm font-medium text-foreground mb-1">Add New Keyword</label>
        <div class="flex gap-2">
          <Input
            id="new-keyword"
            v-model="newKeyword"
            placeholder="Enter keyword to track"
            @keyup.enter="handleAddKeyword"
            class="w-full"
          />
          <Button @click="handleAddKeyword" class="whitespace-nowrap">
            <i class="fas fa-plus mr-2"></i> Add
          </Button>
        </div>
      </div>
      
      <div class="w-full md:w-auto">
        <label class="block text-sm font-medium text-foreground mb-1">Active Keywords</label>
        <div class="flex flex-wrap gap-2 min-h-[40px]">          <div
            v-for="keyword in keywords"
            :key="keyword"
            class="inline-flex items-center px-3 py-1 rounded-md text-sm bg-primary text-primary-foreground"
          >
            <span>{{ keyword }}</span>
            <button
              @click="$emit('remove-keyword', keyword)"
              class="ml-2 hover:text-primary-foreground/80"
            >
              <i class="fas fa-times text-xs"></i>
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
