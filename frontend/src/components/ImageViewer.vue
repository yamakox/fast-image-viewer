<script setup lang="ts">
import { ref, computed, onUnmounted, type Ref, type ComputedRef, watch } from 'vue'
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

const MIN_SCALE = 1
const MAX_SCALE = 5
const WHEEL_ZOOM_STEP = 0.1

const imageScale: Ref<number> = ref(1)
const translateX: Ref<number> = ref(0)
const translateY: Ref<number> = ref(0)
const imageTransformStyle = computed(() => ({
  transform: `translate(${translateX.value}px, ${translateY.value}px) scale(${imageScale.value})`,
}))

let isPanning = false
let isTouchPanning = false
let isPinching = false
let hasPointerMoved = false
let panStartX = 0
let panStartY = 0
let panOriginX = 0
let panOriginY = 0
let pinchStartDistance = 0
let pinchStartScale = 1

function updatePan(clientX: number, clientY: number) {
  const dx = clientX - panStartX
  const dy = clientY - panStartY
  if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
    hasPointerMoved = true
  }
  translateX.value = panOriginX + dx
  translateY.value = panOriginY + dy
}

function startPan(clientX: number, clientY: number) {
  panStartX = clientX
  panStartY = clientY
  panOriginX = translateX.value
  panOriginY = translateY.value
  hasPointerMoved = false
}

// サブルーチン
function clampScale(scale: number): number {
  return Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale))
}

function resetImageTransform() {
  imageScale.value = 1
  translateX.value = 0
  translateY.value = 0
  isPanning = false
  isTouchPanning = false
  isPinching = false
  hasPointerMoved = false
}

function getTouchDistance(touches: TouchList): number {
  const dx = touches[0].clientX - touches[1].clientX
  const dy = touches[0].clientY - touches[1].clientY
  return Math.hypot(dx, dy)
}

function handleWheel(event: WheelEvent) {
  const nextScale = clampScale(imageScale.value + (event.deltaY < 0 ? WHEEL_ZOOM_STEP : -WHEEL_ZOOM_STEP))
  imageScale.value = nextScale
  if (nextScale === MIN_SCALE) {
    translateX.value = 0
    translateY.value = 0
  }
}

function handlePointerMove(event: PointerEvent) {
  if (!isPanning) {
    return
  }
  event.preventDefault()
  updatePan(event.clientX, event.clientY)
}

function stopPanning(event: PointerEvent) {
  if (!isPanning) {
    return
  }
  isPanning = false
  const target = event.currentTarget
  if (target instanceof HTMLElement && target.hasPointerCapture(event.pointerId)) {
    target.releasePointerCapture(event.pointerId)
  }
}

function handlePointerDown(event: PointerEvent) {
  if (isPinching || imageScale.value <= MIN_SCALE || event.button !== 0 || event.pointerType === 'touch') {
    return
  }
  isPanning = true
  startPan(event.clientX, event.clientY)
  const target = event.currentTarget
  if (target instanceof HTMLElement) {
    target.setPointerCapture(event.pointerId)
  }
}

function handleTouchStart(event: TouchEvent) {
  if (event.touches.length === 2) {
    isTouchPanning = false
    isPinching = true
    hasPointerMoved = true
    pinchStartDistance = getTouchDistance(event.touches)
    pinchStartScale = imageScale.value
    return
  }
  if (event.touches.length === 1 && imageScale.value > MIN_SCALE) {
    isTouchPanning = true
    startPan(event.touches[0].clientX, event.touches[0].clientY)
  }
}

function handleTouchMove(event: TouchEvent) {
  if (isPinching && event.touches.length === 2) {
    event.preventDefault()
    const nextScale = clampScale(pinchStartScale * (getTouchDistance(event.touches) / pinchStartDistance))
    imageScale.value = nextScale
    if (nextScale === MIN_SCALE) {
      translateX.value = 0
      translateY.value = 0
    }
    return
  }
  if (isTouchPanning && event.touches.length === 1 && imageScale.value > MIN_SCALE) {
    event.preventDefault()
    updatePan(event.touches[0].clientX, event.touches[0].clientY)
  }
}

function handleTouchEnd(event: TouchEvent) {
  if (event.touches.length < 2) {
    isPinching = false
  }
  if (event.touches.length === 0) {
    isTouchPanning = false
  }
}

function handleStageClick() {
  if (hasPointerMoved) {
    hasPointerMoved = false
    return
  }
  navbarVisible.value = !navbarVisible.value
}

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
    resetImageTransform()
  }
)

watch(imageUrl, () => {
  resetImageTransform()
})

onUnmounted(() => {
  isPanning = false
  isTouchPanning = false
  isPinching = false
})
</script>

<template>
  <div class="image-viewer">
    <!-- 画像 -->
    <div
      class="image-stage"
      :class="{ 'image-stage--draggable': imageScale > MIN_SCALE }"
      @wheel.prevent.stop="handleWheel"
      @pointerdown.stop="handlePointerDown"
      @pointermove="handlePointerMove"
      @pointerup="stopPanning"
      @pointercancel="stopPanning"
      @touchstart.stop="handleTouchStart"
      @touchmove.prevent="handleTouchMove"
      @touchend.stop="handleTouchEnd"
      @touchcancel.stop="handleTouchEnd"
      @click.stop="handleStageClick"
    >
      <img
        :src="imageUrl"
        :alt="imageName"
        class="image-content z-10"
        :style="imageTransformStyle"
        draggable="false"
      />
    </div>

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

.image-stage {
  display: flex;
  width: 100%;
  height: 100%;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  touch-action: none;
}

.image-stage--draggable {
  cursor: grab;
}

.image-stage--draggable:active {
  cursor: grabbing;
}

.image-content {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  transform-origin: center center;
  user-select: none;
}
</style>
