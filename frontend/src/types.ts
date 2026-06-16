export interface Folder {
  id: number | null
  name: string
  pathname: string
  parent: number | null
}

export interface FolderListItem {
  id: number
  name: string
}

export interface ImageListItem {
  id: number
  name: string
  favorite: string | null
}

export interface ImageListPage {
  count: number
  page: number
  num_pages: number
  page_size: number
  results: ImageListItem[]
}

export interface Image {
  id: number
  name: string
  parent: number | null
  hash: string
  timestamp: string
  favorite: string | null
}
