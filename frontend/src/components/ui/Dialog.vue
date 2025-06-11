<template>
  <Teleport to="body">
    <div 
      v-if="open"
      class="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm"
      @click="$emit('close')"
    >
      <div 
        class="fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg duration-200 sm:rounded-lg md:w-full"
        @click.stop
      >
        <slot />
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
interface Props {
  open: boolean
}

defineProps<Props>()
defineEmits<{
  close: []
}>()
</script>
