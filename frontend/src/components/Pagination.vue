<script setup lang="ts">
import { computed, type ComputedRef } from 'vue'

// プロパティ定義
interface Props {
  page: number
  numOfPages: number
}

const props = withDefaults(defineProps<Props>(), {
  page: 1,
  numOfPages: 1,
})

// イベント定義
const emit = defineEmits<{
  pageClick: [page: number]
}>()

//  定数
const DISPLAYINGPAGECOUNT_DELTA: number = 2
const MAX_DISPLAYINGPAGECOUNT: number = DISPLAYINGPAGECOUNT_DELTA * 2 + 1

// ref変数
const displayingPageCount: ComputedRef<number> = computed(() => Math.min(MAX_DISPLAYINGPAGECOUNT, props.numOfPages))
const startPage: ComputedRef<number> = computed(() =>
  Math.max(1, Math.min(props.numOfPages - (displayingPageCount.value - 1), props.page - DISPLAYINGPAGECOUNT_DELTA))
)
const displayingPages: ComputedRef<number[]> = computed(() => {
  const pages: number[] = []
  for (let i = 0; i < displayingPageCount.value; i++) {
    pages.push(startPage.value + i)
  }
  return pages
})

// サブルーチン
/* 未使用のためコメントアウト
function incrementDisplayingPages(n: number) {
  startPage.value = Math.max(
    1,
    Math.min(props.numOfPages - (displayingPageCount.value - 1), startPage.value + n * displayingPageCount.value)
  )
}
*/

function firePageButtonClickEvent(n: number) {
  if (n < 1 || n > props.numOfPages) {
    return
  }
  console.log(`ページ番号: ${n}`)
  emit('pageClick', n)
}
</script>

<template>
  <nav aria-label="Page navigation example">
    <ul class="flex items-center justify-center -space-x-px text-sm">
      <li>
        <button
          @click="firePageButtonClickEvent(props.page - 1)"
          class="text-body bg-neutral-secondary-medium border-default-medium hover:bg-neutral-tertiary-medium hover:text-heading rounded-s-base box-border flex h-10 w-10 items-center justify-center border text-sm font-medium focus:outline-none"
        >
          <span class="sr-only">Previous</span>
          <svg
            class="h-4 w-4 rtl:rotate-180"
            aria-hidden="true"
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            fill="none"
            viewBox="0 0 24 24"
          >
            <path
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="m15 19-7-7 7-7"
            />
          </svg>
        </button>
      </li>
      <li v-for="page in displayingPages" :key="page">
        <button
          v-if="page === props.page"
          aria-current="page"
          class="text-fg-brand bg-neutral-quaternary-medium border-default-medium hover:text-fg-brand box-border flex h-10 w-10 items-center justify-center border text-sm font-medium focus:outline-none"
        >
          {{ page }}
        </button>
        <button
          v-else
          @click="firePageButtonClickEvent(page)"
          class="text-body bg-neutral-secondary-medium border-default-medium hover:bg-neutral-tertiary-medium hover:text-heading box-border flex h-10 w-10 items-center justify-center border text-sm font-medium focus:outline-none"
        >
          {{ page }}
        </button>
      </li>
      <button
        @click="firePageButtonClickEvent(props.page + 1)"
        class="text-body bg-neutral-secondary-medium border-default-medium hover:bg-neutral-tertiary-medium hover:text-heading rounded-e-base box-border flex h-10 w-10 items-center justify-center border text-sm font-medium focus:outline-none"
      >
        <span class="sr-only">Next</span>
        <svg
          class="h-4 w-4 rtl:rotate-180"
          aria-hidden="true"
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          fill="none"
          viewBox="0 0 24 24"
        >
          <path
            stroke="currentColor"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="m9 5 7 7-7 7"
          />
        </svg>
      </button>
    </ul>
  </nav>
</template>
