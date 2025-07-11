<template>
  <section>
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold">Recent Advertisements</h2>
      
      <!-- Controls -->
      <div class="flex items-center space-x-4">
        <div class="flex items-center space-x-2">
          <label class="text-sm text-muted-foreground">Show:</label>
          <select 
            :value="limit" 
            @change="$emit('limit-change', parseInt(($event.target as HTMLSelectElement).value))"
            class="text-sm border rounded px-2 py-1 bg-background"
          >
            <option value="50">50 ads</option>
            <option value="100">100 ads</option>
            <option value="200">200 ads</option>
            <option value="500">All ads</option>
          </select>
        </div>
        
        <div class="flex items-center space-x-2">
          <input 
            type="checkbox" 
            id="show-deleted"
            :checked="includeDeleted"
            @change="$emit('deleted-toggle', ($event.target as HTMLInputElement).checked)"
            class="rounded"
          />
          <label for="show-deleted" class="text-sm text-muted-foreground">Show deleted</label>
        </div>
      </div>
    </div>
    
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
      <!-- Skeleton loading -->
      <Card v-for="i in 6" :key="i">
        <div class="skeleton h-48 w-full"></div>
        <div class="p-4">
          <div class="skeleton h-6 w-3/4 mb-2"></div>
          <div class="skeleton h-4 w-1/2 mb-4"></div>
          <div class="skeleton h-20 w-full mb-4"></div>
          <div class="skeleton h-6 w-1/3"></div>
        </div>
      </Card>
    </div>
    
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 mb-6">
      <AdCard
        v-for="ad in ads"
        :key="ad.id"
        :ad="ad"
        :keyword="ad.keyword"
        @favorite="$emit('favorite', ad)"
      />
    </div>
    
    <div v-if="!loading && ads.length === 0" class="text-center py-10">
      <div class="text-muted-foreground mb-3">
        <i class="fas fa-search fa-3x"></i>
      </div>
      <h3 class="text-lg font-medium text-foreground">No recent ads found</h3>
      <p class="text-muted-foreground">Add some keywords to start tracking ads</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import Card from './ui/Card.vue'
import AdCard from './AdCard.vue'

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
  ads: Ad[]
  loading: boolean
  limit: number
  includeDeleted: boolean
}

defineProps<Props>()
defineEmits<{
  favorite: [ad: Ad]
  'limit-change': [limit: number]
  'deleted-toggle': [includeDeleted: boolean]
}>()
</script>
