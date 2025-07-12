<template>  <Card 
    :class="cardClasses"
  >    <!-- Image -->
    <div class="h-40 bg-muted relative overflow-hidden">
      <img
        v-if="imageUrl && imageUrl !== 'N/A' && imageUrl !== '' && !imageError"
        :src="imageUrl"
        :alt="ad.title"
        :class="imageClasses"
        @error="handleImageError"
        @load="imageLoaded = true"
      />
      <div v-else-if="imageError" class="w-full h-full flex flex-col items-center justify-center text-muted-foreground">
        <i class="fas fa-exclamation-triangle fa-lg mb-2 text-yellow-500"></i>
        <span class="text-xs mb-2">Image failed to load</span>
        <button 
          @click="retryImage" 
          class="text-xs text-primary hover:underline"
        >
          Retry
        </button>
      </div>
      <div v-else class="w-full h-full flex items-center justify-center text-muted-foreground">
        <i class="fas fa-image fa-2x"></i>
      </div>
      
      <!-- Badges -->
      <div class="absolute top-2 right-2 flex flex-col space-y-1">
        <div v-if="ad.isNew" class="bg-primary text-primary-foreground text-xs px-2 py-1 rounded-full font-semibold">
          NEW
        </div>
        <div v-if="ad.is_deleted" class="bg-red-500 text-white text-xs px-2 py-1 rounded-full font-semibold">
          DELETED
        </div>
      </div>
    </div>    <!-- Content -->
    <div class="p-4 flex flex-col flex-grow"><div class="flex justify-between items-start mb-2">
        <h3 class="font-semibold text-sm line-clamp-2 flex-1">{{ displayTitle }}</h3>
        <button
          @click="handleFavorite"
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
      </div>        <p class="text-sm text-muted-foreground mb-2 line-clamp-3 h-16">
        {{ truncatedDescription }}
      </p>
      <!-- Keyword badge under description -->
      <div v-if="keyword" class="mb-2">
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
  is_deleted?: boolean  // Whether the ad has been deleted
  keyword?: string    // Associated keyword
}

interface Props {
  ad: Ad
  keyword?: string
  isFavorite?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  favorite: [ad: Ad]
}>()

const imageLoaded = ref(false)
const imageError = ref(false)
const retryCount = ref(0)
const maxRetries = 2

const handleFavorite = () => {
  if (props.ad && props.ad.id) {
    emit('favorite', props.ad)
  } else {
    console.error('Cannot favorite ad: missing ad or ad.id', props.ad)
  }
}

const displayTitle = computed(() => {
  if (!props.ad.title || props.ad.title === 'Bazos.cz Advertisement' || props.ad.title === 'No title') {
    return 'Untitled Advertisement'
  }
  return props.ad.title
})

const truncatedDescription = computed(() => {
  const description = props.ad.description || 'No description available'
  // Limit to approximately 150 characters (roughly 3 lines)
  const maxLength = 150
  
  if (description.length <= maxLength) {
    return description
  }
  
  // Find the last space before the limit to avoid cutting words
  const truncated = description.substring(0, maxLength)
  const lastSpace = truncated.lastIndexOf(' ')
  
  if (lastSpace > maxLength * 0.8) { // Only use space if it's not too far back
    return truncated.substring(0, lastSpace) + '...'
  }
  
  return truncated + '...'
})

const imageUrl = computed(() => {
  const originalUrl = props.ad.image_url || props.ad.image
  
  // If no image URL, return empty
  if (!originalUrl || originalUrl === 'N/A' || originalUrl === '') {
    return ''
  }
  
  // If it's a relative URL or already from our domain, use as-is
  if (originalUrl.startsWith('/') || originalUrl.includes(window.location.hostname)) {
    return originalUrl
  }
  
  // For external images, use the proxy to avoid CORS issues
  if (originalUrl.startsWith('http://') || originalUrl.startsWith('https://')) {
    return `/api/image-proxy?url=${encodeURIComponent(originalUrl)}`
  }
  
  return originalUrl
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

const handleImageError = () => {
  console.log('Image failed to load:', imageUrl.value, `(retry ${retryCount.value}/${maxRetries})`)
  
  if (retryCount.value < maxRetries) {
    retryCount.value++
    console.log(`Retrying image load... (${retryCount.value}/${maxRetries})`)
    
    // Try to reload the image after a short delay
    setTimeout(() => {
      const img = document.querySelector(`[src="${imageUrl.value}"]`) as HTMLImageElement
      if (img) {
        img.src = imageUrl.value + `&retry=${retryCount.value}`
      }
    }, 1000 * retryCount.value) // Exponential backoff: 1s, 2s
  } else {
    imageError.value = true
    console.log('Image failed to load after all retries:', imageUrl.value)
  }
}

const retryImage = () => {
  imageError.value = false
  retryCount.value = 0
  imageLoaded.value = false
  console.log('Manual retry for image:', imageUrl.value)
}

const cardClasses = computed(() => {
  const classes = ['ad-card-transition', 'overflow-hidden', 'flex', 'flex-col', 'h-full']
  
  if (props.ad.isNew) {
    classes.push('notification-badge', 'ring-2', 'ring-primary')
  }
  
  if (props.ad.is_deleted) {
    classes.push('opacity-60', 'border-red-200', 'dark:border-red-800')
  }
  
  return classes.join(' ')
})

const imageClasses = computed(() => {
  const classes = ['w-full', 'h-full', 'object-cover']
  
  if (props.ad.is_deleted) {
    classes.push('grayscale')
  }
  
  return classes.join(' ')
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-clamp: 2;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-clamp: 3;
  height: 4rem; /* Fixed height for exactly 3 lines (64px) */
  line-height: 1.33rem; /* Approximately 21.33px per line for text-sm */
}

.line-clamp-4 {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-clamp: 4;
}

.ad-card-transition {
  min-height: 400px; /* Restore taller minimum height */
  max-height: 480px; /* Restore taller maximum height */
}
</style>
