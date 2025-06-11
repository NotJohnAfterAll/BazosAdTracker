<template>
  <section>
    <h2 class="text-xl font-semibold mb-4">Changes Log</h2>
    
    <div class="flex gap-4 mb-4">
      <Button
        :variant="filter === 'new' ? 'default' : 'secondary'"
        @click="$emit('filter-change', 'new')"
      >
        <i class="fas fa-plus-circle mr-2"></i> New Ads
      </Button>
      <Button
        :variant="filter === 'deleted' ? 'default' : 'secondary'"
        @click="$emit('filter-change', 'deleted')"
      >
        <i class="fas fa-trash mr-2"></i> Deleted Ads
      </Button>
      <Button
        :variant="filter === 'all' ? 'default' : 'secondary'"
        @click="$emit('filter-change', 'all')"
      >
        <i class="fas fa-sync mr-2"></i> All Changes
      </Button>
    </div>
    
    <div v-if="filteredChanges.length > 0" class="space-y-4">
      <Card
        v-for="change in filteredChanges"
        :key="`${change.timestamp}-${change.ad.id}`"
        class="p-4"
      >
        <div class="flex items-start gap-4">
          <div 
            :class="[
              'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm',
              change.type === 'new' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
            ]"
          >
            <i :class="change.type === 'new' ? 'fas fa-plus' : 'fas fa-minus'"></i>
          </div>
          
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span 
                :class="[
                  'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                  change.type === 'new' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                ]"
              >
                {{ change.type === 'new' ? 'NEW' : 'DELETED' }}
              </span>
              <span class="text-xs text-muted-foreground">{{ change.timestamp }}</span>
            </div>
            
            <div class="text-sm text-muted-foreground mb-1">
              Keyword: <span class="font-medium text-foreground">{{ change.keyword }}</span>
            </div>
            
            <h4 class="font-medium text-sm mb-2">{{ change.ad.title || 'Untitled Advertisement' }}</h4>
            
            <div class="text-sm text-muted-foreground">
              <div class="flex items-center gap-4">
                <span>{{ change.ad.price || 'Price not specified' }}</span>
                <span>{{ cleanSellerName(change.ad.seller_name) }}</span>
                <a
                  :href="change.ad.link"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-primary hover:underline"
                >
                  View <i class="fas fa-external-link-alt ml-1"></i>
                </a>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
    
    <div v-else class="text-center py-10">
      <div class="text-muted-foreground mb-3">
        <i class="fas fa-history fa-3x"></i>
      </div>
      <h3 class="text-lg font-medium text-foreground">No changes detected yet</h3>
      <p class="text-muted-foreground">Changes will appear here when new ads are found or old ones are removed</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Card from './ui/Card.vue'
import Button from './ui/Button.vue'

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

interface Change {
  timestamp: string
  type: 'new' | 'deleted'
  keyword: string
  ad: Ad
}

interface Props {
  changes: Change[]
  filter: 'all' | 'new' | 'deleted'
}

const props = defineProps<Props>()
defineEmits<{
  'filter-change': [filter: 'all' | 'new' | 'deleted']
}>()

const filteredChanges = computed(() => {
  if (props.filter === 'all') {
    return props.changes
  }
  return props.changes.filter(change => change.type === props.filter)
})

const cleanSellerName = (sellerName: string) => {
  if (!sellerName || sellerName === 'N/A') {
    return 'Unknown seller'
  }
  
  // Remove "... bazar pro každého" text
  return sellerName.replace(/\.\.\.\s*bazar\s+pro\s+každého/i, '').trim() || 'Unknown seller'
}
</script>
