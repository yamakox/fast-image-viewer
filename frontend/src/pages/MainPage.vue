<script setup lang="ts">
import FolderOpenIcon from '../components/FolderOpenIcon.vue'
import AngleLeftIcon from '../components/AngleLeftIcon.vue'
import { watch, computed, ref, type Ref, type ComputedRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getData, getThumbnailUrl, getImageUrl } from '../util'
import type { Folder, FolderListItem, ImageListPage } from '../types'
import FolderMenuItem from '../components/FolderMenuItem.vue'
import Pagination from '../components/Pagination.vue'

// Vue Router
const route = useRoute()
const router = useRouter()

// ref変数
const currentFolder: Ref<Folder | null> = ref(null)
const linkToParent: ComputedRef<string | null> = computed(() => {
  if (currentFolder.value?.id === null) {
    return null
  }
  return currentFolder.value?.parent ? `/?parent=${currentFolder.value.parent}` : '/'
})
const folders: Ref<FolderListItem[]> = ref([])
const thumbnails: Ref<ImageListPage | null> = ref(null)
const page: Ref<number> = ref(1)
const numOfPages: Ref<number> = ref(1)

// 型定義
interface FoldersQuery {
  parent?: string
  rootonly?: string
  page?: string
  favoriteonly?: string
}

async function loadPageData() {
  console.log('route.query:', route.query)

  // 現在のフォルダーの取得
  if (route.query.parent) {
    currentFolder.value = (await getData(`/api/v1/folders/${route.query.parent}`)) as Folder | null
    if (currentFolder.value === null) {
      location.href = '/'
      return
    }
  } else {
    currentFolder.value = {
      id: null,
      name: 'Fast Image Viewer',
      pathname: '',
      parent: null,
    }
  }

  // サブフォルダーの取得
  const params: FoldersQuery = route.query.parent ? { parent: route.query.parent as string } : { rootonly: 'yes' }
  folders.value = ((await getData('/api/v1/folders', params)) as FolderListItem[]) ?? []

  // サムネイルの取得
  if (route.query.page) {
    params.page = route.query.page as string
  }
  thumbnails.value = (await getData('/api/v1/images', params)) as ImageListPage | null
  page.value = thumbnails.value?.page ?? 1
  numOfPages.value = thumbnails.value?.num_pages ?? 1
}

watch(
  () => route.fullPath,
  () => {
    loadPageData()
  },
  { immediate: true },
)

// ページネーションのクリックイベントの処理
function handlePageClick(page: number) {
  router.push({ query: { ...route.query, page: page.toString() } })
}
</script>

<template>
  <div class="main-page-container">
    <!-- 半透明なNavbar -->
    <nav
      class="fixed top-0 z-50 w-full translate-y-0 bg-white/50 dark:bg-dark/50 backdrop-blur-sm transition-transform md:hidden md:-translate-y-full"
    >
      <div class="px-3 py-2 lg:px-5 lg:pl-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center justify-start space-x-4 rtl:justify-end">
            <a
              v-if="linkToParent"
              :href="linkToParent"
              class="text-heading rounded-full bg-white p-1.5 text-center text-sm leading-5 font-medium ring-1 ring-gray-200 drop-shadow-lg dark:bg-gray-700 dark:ring-gray-500"
            >
              <angle-left-icon />
            </a>
            <button v-if="folders.length > 0"
              data-drawer-target="main-sidebar"
              data-drawer-toggle="main-sidebar"
              aria-controls="main-sidebar"
              type="button"
              class="text-heading rounded-full bg-white p-1.5 text-center text-sm leading-5 font-medium ring-1 ring-gray-200 drop-shadow-lg dark:bg-gray-700 dark:ring-gray-500"
            >
              <svg
                class="h-6 w-6"
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                fill="none"
                viewBox="0 0 24 24"
              >
                <path stroke="currentColor" stroke-linecap="round" stroke-width="2" d="M5 7h14M5 12h14M5 17h10" />
              </svg>
            </button>
          </div>
          <div class="flex items-center justify-center">
            <div class="text-heading flex items-center justify-center text-sm font-medium">
              <folder-open-icon class="shrink-0" />
              <span class="ms-1 min-w-0 truncate" :title="currentFolder?.name">{{ currentFolder?.name }}</span>
            </div>
          </div>
          <div class="flex items-center justify-end">
            <div class="h-6 w-6"></div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Sidebar -->
    <aside
      id="main-sidebar"
      class="bg-neutral-primary-soft border-default fixed top-0 left-0 z-40 h-full w-64 transition-transform -translate-x-full border-e pt-14 md:translate-x-0 md:pt-0"
      aria-label="Sidebar"
    >
      <div class="h-full overflow-y-auto px-3 py-0">
        <!-- 現在のフォルダー -->
        <ul class="border-default m-0 hidden space-y-2 border-b py-2 font-light md:block">
          <li>
            <div class="text-heading rounded-base group flex min-w-0 items-center px-2 py-1.5">
              <a v-if="linkToParent" :href="linkToParent" class="flex items-center justify-start">
                <div class="text-heading shrink-0 pr-1 text-center text-sm font-medium">
                  <angle-left-icon />
                </div>
                <folder-open-icon class="shrink-0" />
                <span class="ms-1 min-w-0 truncate" :title="currentFolder?.name">{{ currentFolder?.name }}</span>
              </a>
              <div v-else class="flex items-center justify-start">
                <folder-open-icon class="shrink-0" />
                <span class="ms-1 min-w-0 truncate" :title="currentFolder?.name">{{ currentFolder?.name }}</span>
              </div>
            </div>
          </li>
        </ul>

        <!-- サブフォルダー -->
        <ul class="m-0 space-y-2 py-2 font-light">
          <li v-for="folder in folders" :key="folder.id">
            <folder-menu-item :id="folder.id" :name="folder.name" />
          </li>
        </ul>
      </div>
    </aside>

    <div class="mt-14 ml-0 md:mt-0 md:ml-64 flex flex-col items-center justify-start">
      <!-- サムネイル -->
      <div class="flex flex-wrap items-center justify-center gap-0.5 sm:gap-1 py-4 px-1">
        <a
          v-for="thumbnail in thumbnails?.results ?? []"
          :key="thumbnail.id"
          :href="getImageUrl(thumbnail.id)"
          target="_blank"
        >
          <img :src="getThumbnailUrl(thumbnail.id)" :alt="thumbnail.name" class="w-12 h-12 sm:rounded-base sm:w-24 sm:h-24" />
        </a>
      </div>

      <!-- フォルダー内の画像の総数 -->
      <div class="text-body text-sm font-light text-center">
        {{ thumbnails?.count }} images
      </div>

      <!-- ページネーション -->
      <pagination :page="page" :numOfPages="numOfPages" @page-click="handlePageClick" class="m-0 py-4" />
    </div>
  </div>
</template>

<style scoped>
.main-page-container {
  margin: 0;
  padding: 0;
}
</style>
