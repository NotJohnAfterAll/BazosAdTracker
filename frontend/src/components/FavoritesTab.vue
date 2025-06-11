<template>
  <section>
    <h2 class="text-xl font-semibold mb-4">Favorite Advertisements</h2>
    
    <div v-if="favorites.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 mb-6">
      <AdCard
        v-for="ad in favorites"
        :key="ad.id"
        :ad="ad"
        :is-favorite="true"
        @favorite="$emit('favorite', ad)"
      />
    </div>
    
    <!-- No favorites message -->
    <div v-else class="text-center py-10">
      <div class="text-yellow-400 mb-3">
        <i class="fas fa-star fa-3x"></i>
      </div>
      <h3 class="text-lg font-medium text-foreground">No favorites yet</h3>
      <p class="text-muted-foreground">Click the star icon on ads to add them to favorites</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import AdCard from './AdCard.vue'

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
  favorites: Ad[]
}

defineProps<Props>()
defineEmits<{
  favorite: [ad: Ad]
}>()
</script>
