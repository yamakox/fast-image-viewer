<template>
  <div class="folder-menu-item">
    <a
      :href="`/?parent=${props.id}`"
      class="text-heading rounded-base hover:bg-neutral-tertiary hover:text-fg-brand group flex flex-col items-stretch px-2 py-1.5 text-sm"
    >
      <div class="flex min-w-0 items-center justify-start">
        <folder-icon class="shrink-0" />
        <span class="ms-1 min-w-0 truncate" :title="props.name">{{ props.name }}</span>
      </div>
      <div class="flex items-center justify-end gap-0.5">
        <img
          v-for="thumbnail in thumbnails?.results ?? []"
          :key="thumbnail.id"
          :src="getThumbnailUrl(thumbnail.id)"
          :alt="thumbnail.name"
          class="h-8 w-8"
        />
      </div>
    </a>
  </div>
</template>

<script setup lang="ts">
import FolderIcon from './FolderIcon.vue'
import type { ImageListPage } from '../types'
import { getData, getThumbnailUrl } from '../util'
import { onMounted, ref, type Ref } from 'vue'

interface Props {
  id?: number
  name?: string
}

const props = withDefaults(defineProps<Props>(), {
  id: undefined,
  name: undefined,
})

const thumbnails: Ref<ImageListPage | null> = ref(null)
async function fetchThumbnails() {
  const params = {
    parent: props.id,
    ordering: '-favorite,-timestamp',
    page_size: 5,
  }
  thumbnails.value = (await getData('/api/v1/images', params)) as ImageListPage | null
}

onMounted(async () => {
  await fetchThumbnails()
})
</script>

<style scoped>
.folder-menu-item {
  margin: 0;
  padding: 0;
}
</style>
