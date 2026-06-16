<script setup lang="ts">
import { ref, computed, type Ref, type ComputedRef } from 'vue'

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
const startPage: Ref<number> = ref(Math.max(1, props.page - DISPLAYINGPAGECOUNT_DELTA))
const displayingPageCount: ComputedRef<number> = computed(() => Math.min(MAX_DISPLAYINGPAGECOUNT, props.numOfPages))
const displayingPages: ComputedRef<number[]> = computed(() => {
  const pages: number[] = []
  for (let i = 0; i < displayingPageCount.value; i++) {
    pages.push(startPage.value + i)
  }
  return pages
})

// サブルーチン
function incrementDisplayingPages(n: number) {
  startPage.value = Math.max(1, Math.min(props.numOfPages - (displayingPageCount.value - 1), startPage.value + n * displayingPageCount.value))
}

function firePageButtonClickEvent(n: number) {
  console.log(`ページ番号: ${n}`)
  emit('pageClick', n)
}

</script>

<template>
  <nav aria-label="Page navigation example">
    <ul class="flex -space-x-px text-sm items-center justify-center">
      <li>
        <button @click="incrementDisplayingPages(-1)" class="flex items-center justify-center text-body bg-neutral-secondary-medium box-border border border-default-medium hover:bg-neutral-tertiary-medium hover:text-heading font-medium rounded-s-base text-sm w-10 h-10 focus:outline-none">
          <span class="sr-only">Previous</span>
          <svg class="w-4 h-4 rtl:rotate-180" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m15 19-7-7 7-7"/></svg>
        </button>
      </li>
      <li v-for="page in displayingPages" :key="page">
        <button v-if="page === props.page" aria-current="page" class="flex items-center justify-center text-fg-brand bg-neutral-tertiary-medium box-border border border-default-medium hover:text-fg-brand font-medium text-sm w-10 h-10 focus:outline-none">{{ page }}</button>
        <button v-else @click="firePageButtonClickEvent(page)" class="flex items-center justify-center text-body bg-neutral-secondary-medium box-border border border-default-medium hover:bg-neutral-tertiary-medium hover:text-heading font-medium text-sm w-10 h-10 focus:outline-none">{{ page }}</button>
      </li>
      <button @click="incrementDisplayingPages(1)" class="flex items-center justify-center text-body bg-neutral-secondary-medium box-border border border-default-medium hover:bg-neutral-tertiary-medium hover:text-heading font-medium rounded-e-base text-sm w-10 h-10 focus:outline-none">
        <span class="sr-only">Next</span>
        <svg class="w-4 h-4 rtl:rotate-180" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m9 5 7 7-7 7"/></svg>
      </button>
    </ul>
  </nav>
</template>
