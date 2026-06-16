<script setup lang="ts">
import { ref, computed, type Ref, type ComputedRef, watch } from 'vue'
import { getImageUrl, patchData } from '../util'
import type { ImageListItem } from '../types'

// プロパティ定義
interface Props {
  index?: number
  images: ImageListItem[]
}

const props = withDefaults(defineProps<Props>(), {
  index: undefined,
  images: () => [],
})

// イベント定義
const emit = defineEmits<{
  close: []
}>()

// ref変数
const imageIndex: Ref<number | undefined> = ref(props.index)
const navbarVisible: Ref<boolean> = ref(true)
const imageUrl: ComputedRef<string> = computed(() => {
  const image = getIndexedImage(imageIndex.value)
  if (image === undefined) {
    return ''
  }
  return getImageUrl(image.id)
})
const imageName: ComputedRef<string> = computed(() => {
  const image = getIndexedImage(imageIndex.value)
  if (image === undefined) {
    return 'Image'
  }
  return image.name
})
const imageFavorite: ComputedRef<string | null> = computed(() => {
  const image = getIndexedImage(imageIndex.value)
  if (image === undefined) {
    return null
  }
  return image.favorite
})

// サブルーチン
function fireCloseEvent() {
  emit('close')
}

function getIndexedImage(index: number | undefined): ImageListItem | undefined {
  if (index === undefined) {
    return undefined
  }
  return props.images[index]
}

function incrementImageIndex(n: number): boolean {
  if (imageIndex.value === undefined) {
    return false
  }
  imageIndex.value = Math.min(Math.max(0, imageIndex.value + n), props.images.length - 1)
  return false
}

async function toggleFavorite() {
  const image = getIndexedImage(imageIndex.value)
  if (image === undefined) {
    return
  }
  if (image.favorite === null) {
    const dateString = new Date().toISOString()
    const result = await patchData(`/api/v1/images/${image.id}`, { favorite: dateString })
    if (result === null) {
      return
    }
    image.favorite = result.favorite
  } else {
    const result = await patchData(`/api/v1/images/${image.id}`, { favorite: null })
    if (result === null) {
      return
    }
    image.favorite = result.favorite
  }
}

watch(
  () => props.index,
  () => {
    navbarVisible.value = true
  }
)
</script>

<template>
  <div class="image-viewer" @click="navbarVisible = !navbarVisible">
    <!-- 画像 -->
    <img :src="imageUrl" :alt="imageName" class="z-10 h-full w-full object-contain" />

    <!-- 上部ナビゲーション -->
    <nav v-if="navbarVisible" class="fixed top-0 z-50 flex w-full items-center justify-end bg-transparent p-4">
      <button class="text-heading text-center text-sm leading-5 font-medium" @click.stop="fireCloseEvent">
        <svg
          class="h-9 w-9 text-gray-800 dark:text-white"
          aria-hidden="true"
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          fill="none"
          viewBox="0 0 24 24"
        >
          <path
            stroke="white"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M6 18 17.94 6M18 18 6.06 6"
          />
        </svg>
      </button>
    </nav>

    <!-- 下部ナビゲーション -->
    <nav v-if="navbarVisible" class="fixed bottom-0 z-50 flex w-full items-center justify-between bg-transparent p-4">
      <button @click.stop="incrementImageIndex(-1)" class="text-heading text-center text-sm leading-5 font-medium">
        <svg
          class="h-9 w-9"
          aria-hidden="true"
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          fill="none"
          viewBox="0 0 24 24"
        >
          <path stroke="white" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m15 19-7-7 7-7" />
        </svg>
      </button>
      <button @click.stop="toggleFavorite" class="text-heading text-center text-sm leading-5 font-medium">
        <svg
          v-if="imageFavorite"
          class="h-9 w-9 text-white"
          aria-hidden="true"
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          fill="none"
          viewBox="0 0 24 24"
        >
          <path
            fill="white"
            d="m12.75 20.66 6.184-7.098c2.677-2.884 2.559-6.506.754-8.705-.898-1.095-2.206-1.816-3.72-1.855-1.293-.034-2.652.43-3.963 1.442-1.315-1.012-2.678-1.476-3.973-1.442-1.515.04-2.825.76-3.724 1.855-1.806 2.201-1.915 5.823.772 8.706l6.183 7.097c.19.216.46.34.743.34a.985.985 0 0 0 .743-.34Z"
          />
        </svg>
        <svg
          v-else
          class="h-9 w-9 text-white"
          aria-hidden="true"
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          fill="none"
          viewBox="0 0 24 24"
        >
          <path
            stroke="white"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12.01 6.001C6.5 1 1 8 5.782 13.001L12.011 20l6.23-7C23 8 17.5 1 12.01 6.002Z"
          />
        </svg>
      </button>
      <button @click.stop="incrementImageIndex(1)" class="text-heading text-center text-sm leading-5 font-medium">
        <svg
          class="h-9 w-9 text-gray-800 dark:text-white"
          aria-hidden="true"
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          fill="none"
          viewBox="0 0 24 24"
        >
          <path stroke="white" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m9 5 7 7-7 7" />
        </svg>
      </button>
    </nav>
  </div>
</template>

<style scoped>
.image-viewer {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background-color: rgba(0, 0, 0, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
