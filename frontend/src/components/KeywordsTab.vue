<template>
  <section>
    <div class="mb-4 flex flex-col sm:flex-row gap-4">
      <div class="flex-1">
        <label for="keyword-filter" class="form-label">Select Keyword</label>
        <Select id="keyword-filter" @change="handleKeywordChange">
          <option value="">Select a keyword...</option>
          <option v-for="keyword in keywords" :key="keyword" :value="keyword">
            {{ keyword }}
          </option>
        </Select>
      </div>
      
      <div class="flex-1">
        <label for="ad-search" class="form-label">Search in Results</label>
        <div class="relative">
          <Input
            id="ad-search"
            v-model="searchQuery"
            placeholder="Search by title, description, price..."
            class="pl-9"
          />
          <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <i class="fas fa-search text-muted-foreground"></i>
          </div>
          <button
            v-if="searchQuery"
            @click="searchQuery = ''"
            class="absolute inset-y-0 right-0 flex items-center pr-3 text-muted-foreground hover:text-foreground"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>
      <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-semibold">
        {{ currentKeyword ? `Advertisements for "${currentKeyword}"` : 'Advertisements by Keyword' }}
      </h2>
      <span class="text-sm text-muted-foreground">{{ filteredAds.length }} results</span>
    </div>
    
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 mb-6">
      <!-- Skeleton loading -->
      <Card v-for="i in 8" :key="i">
        <div class="skeleton h-48 w-full"></div>
        <div class="p-4">
          <div class="skeleton h-6 w-3/4 mb-2"></div>
          <div class="skeleton h-4 w-1/2 mb-4"></div>
          <div class="skeleton h-20 w-full mb-4"></div>
          <div class="skeleton h-6 w-1/3"></div>
        </div>
      </Card>
    </div>
    
    <div v-else-if="currentKeyword" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 mb-6">
      <AdCard
        v-for="ad in paginatedAds"
        :key="ad.id"
        :ad="ad"
        @favorite="$emit('favorite', ad)"
      />
    </div>
    
    <!-- Pagination controls -->
    <div v-if="totalPages > 1" class="flex justify-center items-center mt-6 space-x-2">
      <Button
        variant="secondary"
        :disabled="currentPage === 1"
        @click="currentPage--"
      >
        <i class="fas fa-chevron-left mr-2"></i>Previous
      </Button>
      
      <div class="text-sm text-muted-foreground">
        Page {{ currentPage }} of {{ totalPages }}
      </div>
      
      <Button
        variant="secondary"
        :disabled="currentPage === totalPages"
        @click="currentPage++"
      >
        Next<i class="fas fa-chevron-right ml-2"></i>
      </Button>
    </div>
    
    <!-- No results message -->
    <div v-if="!loading && currentKeyword && filteredAds.length === 0" class="text-center py-10">
      <div class="text-muted-foreground mb-3">
        <i class="fas fa-search fa-3x"></i>
      </div>
      <h3 class="text-lg font-medium text-foreground">No matching advertisements found</h3>
      <p class="text-muted-foreground">Try adjusting your search query</p>
    </div>
    
    <!-- No keyword selected -->
    <div v-if="!loading && !currentKeyword" class="text-center py-10">
      <div class="text-muted-foreground mb-3">
        <i class="fas fa-tags fa-3x"></i>
      </div>
      <h3 class="text-lg font-medium text-foreground">Select a keyword</h3>
      <p class="text-muted-foreground">Choose a keyword from the dropdown to view its advertisements</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Card from './ui/Card.vue'
import Input from './ui/Input.vue'
import Select from './ui/Select.vue'
import Button from './ui/Button.vue'
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
  keywords: string[]
  keywordAds: Ad[]
  loading: boolean
  currentKeyword: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'keyword-select': [keyword: string]
  favorite: [ad: Ad]
}>()

const searchQuery = ref('')
const currentPage = ref(1)
const adsPerPage = 15

const filteredAds = computed(() => {
  if (!searchQuery.value) {
    return props.keywordAds
  }
  
  const query = searchQuery.value.toLowerCase()
  return props.keywordAds.filter(ad => 
    ad.title?.toLowerCase().includes(query) ||
    ad.description?.toLowerCase().includes(query) ||
    ad.price?.toLowerCase().includes(query) ||
    ad.seller_name?.toLowerCase().includes(query)
  )
})

const totalPages = computed(() => Math.ceil(filteredAds.value.length / adsPerPage))

const paginatedAds = computed(() => {
  const start = (currentPage.value - 1) * adsPerPage
  const end = start + adsPerPage
  return filteredAds.value.slice(start, end)
})

const handleKeywordChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  emit('keyword-select', target.value)
  currentPage.value = 1
}

// Reset pagination when search changes
watch(searchQuery, () => {
  currentPage.value = 1
})

// Reset pagination when keyword changes
watch(() => props.currentKeyword, () => {
  currentPage.value = 1
  searchQuery.value = ''
})
</script>
