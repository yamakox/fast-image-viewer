const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL.replace(/\/+$/, '')

function getThumbnailUrl(id: number): string {
  return `${API_BASE_URL}/api/v1/images/${id}/thumbnail`
}

function getImageUrl(id: number): string {
  return `${API_BASE_URL}/api/v1/images/${id}/image`
}

async function getData(url: string, queryParams: any = {}): Promise<any | null> {
  try {
    const response = await fetch(`${API_BASE_URL}${url}?${new URLSearchParams(queryParams).toString()}`)
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

async function patchData(url: string, data: any): Promise<any | null> {
  try {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
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

export { API_BASE_URL, getData, patchData, getThumbnailUrl, getImageUrl }
