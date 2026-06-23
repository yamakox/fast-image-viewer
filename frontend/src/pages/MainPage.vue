<script setup lang="ts">
import FolderOpenIcon from '../components/FolderOpenIcon.vue'
import AngleLeftIcon from '../components/AngleLeftIcon.vue'
import { watch, computed, ref, onMounted, type Ref, type ComputedRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getData, getSession, getThumbnailUrl, postData } from '../util'
import type { Folder, FolderListItem, ImageListPage } from '../types'
import FolderMenuItem from '../components/FolderMenuItem.vue'
import Pagination from '../components/Pagination.vue'
import ImageViewer from '../components/ImageViewer.vue'

// Vue Router
const route = useRoute()
const router = useRouter()

// 定数

// ORDERRING_PARAMETERS[名前順(1/0)][昇順(1/0)] → orderingクエリーパラメータの値
const ORDERING_PARAMETERS: Record<number, Record<number, string | undefined>> = {
  // 名前順
  1: {
    1: 'name',
    0: '-name',
  },
  0: {
    1: 'timestamp',
    0: undefined, // デフォルトの並び順(orderingクエリーパラメータを指定しない)
  },
}

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
const thumbnailIndex: Ref<number | null> = ref(null)
const favoriteOnly: Ref<boolean> = ref(false)
const sortByName: Ref<boolean> = ref(false)
const sortAscending: Ref<boolean> = ref(false)
const isAuthenticated = ref(false)
const username: Ref<string> = ref('')

// 型定義
interface PageQuery {
  parent?: string
  rootonly?: string
  page?: string
  favoriteonly?: string
  ordering?: string
}

// ログインページに移動
function moveToLoginPage() {
  location.href = router.resolve({ name: 'Login' }).href
}

// ページのクエリーパラメータからAPIのクエリーパラメータを生成
function getQueryFromRouteQuery(routeQuery: any /* LocationQuery$1 */): PageQuery {
  const query: PageQuery = { ...routeQuery }
  if (!routeQuery.parent) {
    query.rootonly = 'yes'
  }
  return query
}

// ページデータの読み込み
async function loadPageData() {
  console.log('loadPageData: route.query:', route.query)

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
  const folderParams: PageQuery = getQueryFromRouteQuery(route.query)
  folderParams.ordering = undefined
  folders.value = ((await getData('/api/v1/folders', folderParams)) as FolderListItem[]) ?? []

  // サムネイルの取得
  const imageParams: PageQuery = getQueryFromRouteQuery(route.query)
  thumbnails.value = (await getData('/api/v1/images', imageParams)) as ImageListPage | null
  
  // お気に入りボタンをオンにすると、当該ページ番号が不在になってthumbnails.valueがnullになる場合があるので、ページ番号を消して再読込する
  if (!thumbnails.value) {
    router.push({ query: { ...route.query, page: undefined } })
  }

  page.value = thumbnails.value?.page ?? 1
  numOfPages.value = thumbnails.value?.num_pages ?? 1
}

// ルートの変更を監視して、ページデータを読み込む
watch(
  () => route.fullPath,
  async () => {
    if (isAuthenticated.value) {
      await loadPageData()
    }
  }
)

// マウント時にページデータを読み込む
onMounted(async () => {
  const session = await getSession()
  if (!session) {
    moveToLoginPage()
    return
  }
  username.value = session.username
  isAuthenticated.value = true
  await loadPageData()
})

// クエリー条件変更ボタンのクリックイベントの処理
function handleQueryConditionChange() {
  const ordering = ORDERING_PARAMETERS[sortByName.value ? 1 : 0][sortAscending.value ? 1 : 0]
  router.push({ query: { ...route.query, favoriteonly: favoriteOnly.value ? 'yes' : undefined, ordering: ordering } })
}

// ページネーションのクリックイベントの処理
function handlePageClick(page: number) {
  router.push({ query: { ...route.query, page: page.toString() } })
}

// ログアウトボタンのクリックイベントの処理
async function handleLogout(event: Event) {
  const button = event.currentTarget as HTMLButtonElement
  button.blur()

  const { ok } = await postData('/api/v1/logout', {})
  if (ok) {
    moveToLoginPage()
  }
}
</script>

<template>
  <div v-if="isAuthenticated" class="main-page-container">
    <!-- 半透明なNavbar -->
    <nav
      class="dark:bg-dark/50 fixed top-0 z-50 w-full translate-y-0 bg-white/50 backdrop-blur-sm transition-transform md:hidden md:-translate-y-full"
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
            <button
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
      class="bg-neutral-primary-soft border-default fixed top-0 left-0 z-40 h-full w-64 -translate-x-full border-e pt-14 transition-transform md:translate-x-0 md:pt-0"
      aria-label="Sidebar"
    >
      <div class="flex h-full flex-col justify-between overflow-y-auto px-3 py-0">
        <!-- 現在のフォルダー -->
        <ul class="border-default m-0 space-y-2 border-b py-2 font-light">
          <li class="hidden md:block">
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
          <li>
            <label class="text-heading inline-flex cursor-pointer items-center px-2 py-1.5">
              <input type="checkbox" v-model="favoriteOnly" @change="handleQueryConditionChange" class="peer sr-only" />
              <div
                class="bg-neutral-quaternary peer-focus:ring-brand-soft dark:peer-focus:ring-brand-soft peer peer-checked:after:border-buffer peer-checked:bg-brand relative h-5 w-9 rounded-full peer-focus:ring-4 peer-focus:outline-none after:absolute after:inset-s-[2px] after:top-[2px] after:h-4 after:w-4 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full"
              ></div>
              <span class="text-heading ms-3 text-sm font-medium select-none">♥だけ表示</span>
            </label>
          </li>
          <li>
            <label class="text-heading inline-flex cursor-pointer items-center px-2 py-1.5">
              <input type="checkbox" v-model="sortByName" @change="handleQueryConditionChange" class="peer sr-only" />
              <div
                class="bg-neutral-quaternary peer-focus:ring-brand-soft dark:peer-focus:ring-brand-soft peer peer-checked:after:border-buffer peer-checked:bg-brand relative h-5 w-9 rounded-full peer-focus:ring-4 peer-focus:outline-none after:absolute after:inset-s-[2px] after:top-[2px] after:h-4 after:w-4 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full"
              ></div>
              <span class="text-heading ms-3 text-sm font-medium select-none">名前順で表示</span>
            </label>
          </li>
          <li>
            <label class="text-heading inline-flex cursor-pointer items-center px-2 py-1.5">
              <input
                type="checkbox"
                v-model="sortAscending"
                @change="handleQueryConditionChange"
                class="peer sr-only"
              />
              <div
                class="bg-neutral-quaternary peer-focus:ring-brand-soft dark:peer-focus:ring-brand-soft peer peer-checked:after:border-buffer peer-checked:bg-brand relative h-5 w-9 rounded-full peer-focus:ring-4 peer-focus:outline-none after:absolute after:inset-s-[2px] after:top-[2px] after:h-4 after:w-4 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full"
              ></div>
              <span class="text-heading ms-3 text-sm font-medium select-none">昇順で並べ替え</span>
            </label>
          </li>
        </ul>

        <!-- サブフォルダー -->
        <ul class="border-default m-0 space-y-2 border-b py-2 font-light">
          <li v-for="folder in folders" :key="folder.id">
            <folder-menu-item :id="folder.id" :name="folder.name" />
          </li>
        </ul>

        <!-- ログアウト -->
        <ul class="m-0 mt-auto space-y-2 py-2 font-light">
          <li>
            <div class="folder-menu-item">
              <button
                type="button"
                @click="handleLogout"
                class="text-heading rounded-base hover:bg-neutral-tertiary hover:text-fg-brand group flex w-full items-center justify-center px-2 py-1.5 text-sm"
              >
                <span class="text-heading ms-1 min-w-0 truncate text-sm font-medium" :title="username">{{
                  username
                }}</span>
                <span class="text-heading truncate text-sm">のログアウト</span>
              </button>
            </div>
          </li>
        </ul>
      </div>
    </aside>

    <div class="mt-14 ml-0 flex flex-col items-center justify-start md:mt-0 md:ml-64">
      <!-- サムネイル -->
      <div
        class="grid w-full grid-cols-[repeat(auto-fit,4.5rem)] justify-center gap-0.5 px-1 py-4 sm:grid-cols-[repeat(auto-fit,6rem)] sm:gap-1"
      >
        <a
          v-for="(thumbnail, index) in thumbnails?.results ?? []"
          :key="index"
          class="relative inline-block"
          @click="thumbnailIndex = index"
        >
          <img
            :src="getThumbnailUrl(thumbnail.id)"
            :alt="thumbnail.name"
            class="sm:rounded-base h-18 w-18 sm:h-24 sm:w-24"
          />
          <svg
            v-if="thumbnail.favorite"
            class="absolute right-0 bottom-0 h-6 w-6 text-white"
            aria-hidden="true"
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            fill="none"
            viewBox="0 0 24 24"
          >
            <path
              stroke="black"
              fill="white"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1"
              d="M12.01 6.001C6.5 1 1 8 5.782 13.001L12.011 20l6.23-7C23 8 17.5 1 12.01 6.002Z"
            />
          </svg>
        </a>
      </div>

      <!-- フォルダー内の画像の総数 -->
      <div class="text-body text-center text-sm font-light">{{ thumbnails?.count }} images</div>

      <!-- ページネーション -->
      <pagination :page="page" :numOfPages="numOfPages" @page-click="handlePageClick" class="m-0 py-4" />
    </div>

    <!-- 画像ビューアー -->
    <image-viewer
      v-if="thumbnailIndex !== null"
      :index="thumbnailIndex"
      :images="thumbnails?.results ?? []"
      @close="thumbnailIndex = null"
    />
  </div>
</template>

<style scoped>
.main-page-container {
  margin: 0;
  padding: 0;
}
</style>
