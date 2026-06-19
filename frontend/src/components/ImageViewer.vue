<script setup lang="ts">
import { ref, computed, onUnmounted, type Ref, type ComputedRef, watch } from 'vue'
import { getImageUrl, patchData } from '../util'
import type { ImageListItem } from '../types'
import panzoom, { type PanZoom } from 'panzoom'

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

// 定数
const MIN_ZOOM = 1
const MAX_ZOOM = 5

// ref変数
const imageViewerRef: Ref<HTMLImageElement | null> = ref(null)
const imageRef: Ref<HTMLImageElement | null> = ref(null)
const imageIndex: Ref<number | undefined> = ref(props.index)
const navbarVisible: Ref<boolean> = ref(true)
const isZoomed: Ref<boolean> = ref(false)
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

// グローバル変数
let panzoomInstance: PanZoom | null = null

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

function toggleImageZoom() {
  if (panzoomInstance === null) {
    return
  }
  const transform = panzoomInstance.getTransform()
  console.log('toggleImageZoom', transform.scale)
  const pw = imageViewerRef.value?.clientWidth
  const ph = imageViewerRef.value?.clientHeight
  const iw = imageRef.value?.naturalWidth
  const ih = imageRef.value?.naturalHeight
  if (pw === undefined || ph === undefined || iw === undefined || ih === undefined) {
    return
  }
  console.log(`pw: ${pw}, ph: ${ph}, iw: ${iw}, ih: ${ih}`)
  if (transform.scale <= MIN_ZOOM) {
    const rw = pw / iw
    const rh = ph / ih
    if (rw > rh) {
      panzoomInstance.smoothZoom(pw / 2, ph / 2, rw / rh)
    } else {
      panzoomInstance.smoothZoom(pw / 2, ph / 2, rh / rw)
    }
  } else {
    // NOTE: 第3パラメータは現在のscaleに対してのズーム倍率になるため、
    //       scaleを1に戻すときは逆数を指定する。
    //       minZoomが1、maxZoomが5のため、maxZoomの逆数をかければよい。
    panzoomInstance.smoothZoom(pw / 2, ph / 2, 1.0 / MAX_ZOOM)
  }
}

watch(imageRef, (newVal) => {
  if (newVal === null) {
    return
  }
  panzoomInstance = panzoom(newVal, {
    bounds: true,
    boundsPadding: 1,
    smoothScroll: true,
    minZoom: MIN_ZOOM,
    maxZoom: MAX_ZOOM,
  })
  panzoomInstance.on('zoom', () => {
    const transform = panzoomInstance?.getTransform()
    if (transform === undefined) {
      return
    }
    isZoomed.value = transform.scale > MIN_ZOOM
  })
})

watch(imageUrl, () => {
  if (panzoomInstance === null) {
    return
  }
  const pw = imageViewerRef.value?.clientWidth
  const ph = imageViewerRef.value?.clientHeight
  if (pw === undefined || ph === undefined) {
    return
  }
  panzoomInstance.zoomTo(pw / 2, ph / 2, 1.0 / MAX_ZOOM)
})

onUnmounted(() => {
  if (panzoomInstance !== null) {
    panzoomInstance.dispose()
  }
})
</script>

<template>
  <div ref="imageViewerRef" class="image-viewer" @click.stop="navbarVisible = !navbarVisible">
    <!-- 画像 -->
    <img ref="imageRef" :src="imageUrl" :alt="imageName" class="image-content" />

    <!-- 上部ナビゲーション -->
    <nav v-if="navbarVisible" class="fixed top-0 left-0 right-0 flex w-full items-center justify-between bg-black/20 p-4">
      <button
        class="nav-button text-heading text-center text-sm leading-5 font-medium"
        @click.stop="toggleImageZoom()"
      >
        <svg
          v-if="!isZoomed"
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
            d="M8 4H4m0 0v4m0-4 5 5m7-5h4m0 0v4m0-4-5 5M8 20H4m0 0v-4m0 4 5-5m7 5h4m0 0v-4m0 4-5-5"
          />
        </svg>
        <svg
          v-else
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
            d="M5 9h4m0 0V5m0 4L4 4m15 5h-4m0 0V5m0 4 5-5M5 15h4m0 0v4m0-4-5 5m15-5h-4m0 0v4m0-4 5 5"
          />
        </svg>
      </button>
      <div class="truncate text-center leading-5 font-medium text-white">{{ imageName }}</div>
      <button class="nav-button text-heading text-center text-sm leading-5 font-medium" @click.stop="fireCloseEvent">
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

    <!-- 中央ナビゲーション -->
    <button v-if="navbarVisible"
      @click.stop="incrementImageIndex(-1)"
      class="fixed top-1/2 left-0 text-heading bg-black/20 p-4 text-center text-sm leading-5 font-medium"
    >
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
    <button v-if="navbarVisible"
      @click.stop="incrementImageIndex(1)"
      class="fixed top-1/2 right-0 text-heading bg-black/20 p-4 text-center text-sm leading-5 font-medium"
    >
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

    <!-- 下部ナビゲーション -->
    <nav v-if="navbarVisible"class="fixed bottom-0 left-0 right-0 flex w-full items-center justify-between bg-black/20 p-4">
      <button
        @click.stop="toggleFavorite"
        class="nav-button text-heading ms-auto me-auto text-center text-sm leading-5 font-medium"
      >
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
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.image-content {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
</style>
