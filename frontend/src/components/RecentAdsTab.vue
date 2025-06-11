<template>
  <section>
    <h2 class="text-xl font-semibold mb-4">Recent Advertisements</h2>
    
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
        v-for="item in ads"
        :key="item.ad.id"
        :ad="item.ad"
        :keyword="item.keyword"
        @favorite="$emit('favorite', item.ad)"
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

interface KeywordAd {
  keyword: string
  ad: Ad
}

interface Props {
  ads: KeywordAd[]
  loading: boolean
}

defineProps<Props>()
defineEmits<{
  favorite: [ad: Ad]
}>()
</script>
