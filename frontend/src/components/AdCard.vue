<template>  <Card 
    :class="[
      'ad-card-transition overflow-hidden flex flex-col h-full',
      ad.isNew ? 'notification-badge ring-2 ring-primary' : ''
    ]"
  ><!-- Image -->
    <div class="h-60 bg-muted relative overflow-hidden">
      <img
        v-if="imageUrl && imageUrl !== 'N/A' && imageUrl !== '' && !imageError"
        :src="imageUrl"
        :alt="ad.title"
        class="w-full h-full object-cover"
        @error="handleImageError"
        @load="imageLoaded = true"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-muted-foreground">
        <i class="fas fa-image fa-2x"></i>
      </div>
        <!-- New badge -->
      <div v-if="ad.isNew" class="absolute top-2 right-2 bg-primary text-primary-foreground text-xs px-2 py-1 rounded-full font-semibold">
        NEW
      </div>
    </div>    <!-- Content -->
    <div class="p-4 flex flex-col h-full">      <div class="flex justify-between items-start mb-2">
        <h3 class="font-semibold text-sm line-clamp-2 flex-1">{{ displayTitle }}</h3>
        <button
          @click="$emit('favorite')"
          :class="[
            'ml-2 flex-shrink-0',
            isFavorite ? 'text-yellow-500' : 'text-muted-foreground hover:text-yellow-500'
          ]"
        >
          <i :class="isFavorite ? 'fas fa-star' : 'far fa-star'"></i>
        </button>
      </div>
      
      <div class="text-xs text-muted-foreground mb-2">
        <div>{{ formatDate(ad.date_added) }}</div>
      </div>
      
      <p class="text-sm text-muted-foreground mb-3 line-clamp-3 flex-grow">
        {{ ad.description || 'No description available' }}
      </p>
      
      <!-- Keyword badge under description -->
      <div v-if="keyword" class="mb-3">
        <span class="inline-flex items-center px-2 py-1 rounded text-xs bg-muted text-muted-foreground border font-medium">
          {{ keyword }}
        </span>
      </div>
      
      <!-- Price and link at bottom -->
      <div class="flex justify-between items-center mt-auto">
        <div class="font-bold text-primary">
          {{ ad.price || 'Price not specified' }}
        </div>
        <a
          :href="ad.link"
          target="_blank"
          rel="noopener noreferrer"
          class="text-xs text-primary hover:underline"
        >
          View <i class="fas fa-external-link-alt ml-1"></i>
        </a>
      </div>
    </div>
  </Card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import Card from './ui/Card.vue'

interface Ad {
  id: string
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
}

interface Props {
  ad: Ad
  keyword?: string
  isFavorite?: boolean
}

const props = defineProps<Props>()
defineEmits<{
  favorite: []
}>()

const imageLoaded = ref(false)
const imageError = ref(false)

const displayTitle = computed(() => {
  if (!props.ad.title || props.ad.title === 'Bazos.cz Advertisement' || props.ad.title === 'No title') {
    return 'Untitled Advertisement'
  }
  return props.ad.title
})

const imageUrl = computed(() => {
  // Prefer image_url over image field
  return props.ad.image_url || props.ad.image
})

const cleanSellerName = computed(() => {
  if (!props.ad.seller_name || props.ad.seller_name === 'N/A') {
    return 'Unknown seller'
  }
  
  // Remove "... bazar pro každého" text
  return props.ad.seller_name.replace(/\.\.\.\s*bazar\s+pro\s+každého/i, '').trim() || 'Unknown seller'
})

const formatDate = (dateStr: string) => {
  if (!dateStr || dateStr === 'N/A') {
    return 'Date unknown'
  }
  
  try {
    // Handle Czech date format like "8.6. 2025"
    if (dateStr.includes('.')) {
      const parts = dateStr.trim().replace(' ', '').split('.')
      if (parts.length >= 3) {
        const day = parseInt(parts[0])
        const month = parseInt(parts[1])
        const year = parseInt(parts[2]) || new Date().getFullYear()
        return `${day}.${month}.${year}`
      }
    }
    
    return dateStr
  } catch (error) {
    return dateStr
  }
}

const handleImageError = (event: Event) => {
  imageError.value = true
  console.log('Image failed to load:', imageUrl.value)
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
