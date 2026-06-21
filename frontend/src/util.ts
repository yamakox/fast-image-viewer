const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL.replace(/\/+$/, '')

interface PostDataResult {
  ok: boolean
  result: Record<string, unknown> | null
}

function getCsrfToken(): string | null {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]*)/)
  return match ? decodeURIComponent(match[1]) : null
}

async function ensureCsrfCookie(): Promise<void> {
  if (getCsrfToken()) {
    return
  }
  await fetch(`${API_BASE_URL}/api/v1/folders?rootonly=yes`, { credentials: 'include' })
}

function getThumbnailUrl(id: number): string {
  return `${API_BASE_URL}/api/v1/images/${id}/thumbnail`
}

function getImageUrl(id: number): string {
  return `${API_BASE_URL}/api/v1/images/${id}/image`
}

interface SessionUser {
  id: number
  username: string
}

async function getSession(): Promise<SessionUser | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/session`, { credentials: 'include' })
    if (!response.ok) {
      return null
    }
    return (await response.json()) as SessionUser
  } catch {
    return null
  }
}

async function checkSession(): Promise<boolean> {
  return (await getSession()) !== null
}

async function getData(url: string, queryParams: any = {}): Promise<any | null> {
  try {
    const response = await fetch(`${API_BASE_URL}${url}?${new URLSearchParams(queryParams).toString()}`, {
      credentials: 'include',
    })
    if (!response.ok) {
      throw new Error(`レスポンスステータス: ${response.status}`)
    }

    const result = await response.json()
    console.log(result)
    return result
  } catch (error: any) {
    console.error(error.message)
    return null
  }
}

async function postData(url: string, data: Record<string, string>): Promise<PostDataResult> {
  await ensureCsrfCookie()
  const csrfToken = getCsrfToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (csrfToken) {
    headers['X-CSRFToken'] = csrfToken
  }
  try {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      method: 'POST',
      credentials: 'include',
      headers,
      body: JSON.stringify(data),
    })
    const result = await response.json()
    console.log(result)
    return { ok: response.ok, result }
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error)
    console.error(message)
    return { ok: false, result: null }
  }
}

async function patchData(url: string, data: any): Promise<any | null> {
  await ensureCsrfCookie()
  const csrfToken = getCsrfToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (csrfToken) {
    headers['X-CSRFToken'] = csrfToken
  }
  try {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      method: 'PATCH',
      credentials: 'include',
      headers,
      body: JSON.stringify(data),
    })
    if (!response.ok) {
      throw new Error(`レスポンスステータス: ${response.status}`)
    }

    const result = await response.json()
    console.log(result)
    return result
  } catch (error: any) {
    console.error(error.message)
    return null
  }
}

export { API_BASE_URL, checkSession, ensureCsrfCookie, getData, getSession, postData, patchData, getThumbnailUrl, getImageUrl }
export type { SessionUser }
