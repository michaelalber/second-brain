import type {
  Container,
  ContainerCreate,
  ContainerUpdate,
  ContainerWithCount,
  ContainerWithNotes,
  Note,
  NoteCreate,
  NoteHighlightsUpdate,
  NoteMoveRequest,
  NoteUpdate,
} from '@/types'

const API_BASE = '/api/v1'

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return response.json()
}

// Notes API
export const notesApi = {
  async create(note: NoteCreate): Promise<Note> {
    const response = await fetch(`${API_BASE}/notes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(note),
    })
    return handleResponse<Note>(response)
  },

  async list(params?: {
    container_id?: string
    stage?: string
    q?: string
  }): Promise<Note[]> {
    const searchParams = new URLSearchParams()
    if (params?.container_id) searchParams.set('container_id', params.container_id)
    if (params?.stage) searchParams.set('stage', params.stage)
    if (params?.q) searchParams.set('q', params.q)

    const query = searchParams.toString()
    const url = query ? `${API_BASE}/notes?${query}` : `${API_BASE}/notes`
    const response = await fetch(url)
    return handleResponse<Note[]>(response)
  },

  async get(id: string): Promise<Note> {
    const response = await fetch(`${API_BASE}/notes/${id}`)
    return handleResponse<Note>(response)
  },

  async update(id: string, note: NoteUpdate): Promise<Note> {
    const response = await fetch(`${API_BASE}/notes/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(note),
    })
    return handleResponse<Note>(response)
  },

  async move(id: string, request: NoteMoveRequest): Promise<Note> {
    const response = await fetch(`${API_BASE}/notes/${id}/move`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    })
    return handleResponse<Note>(response)
  },

  async updateHighlights(id: string, highlights: NoteHighlightsUpdate): Promise<Note> {
    const response = await fetch(`${API_BASE}/notes/${id}/highlights`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(highlights),
    })
    return handleResponse<Note>(response)
  },

  async delete(id: string): Promise<void> {
    const response = await fetch(`${API_BASE}/notes/${id}`, {
      method: 'DELETE',
    })
    return handleResponse<void>(response)
  },
}

// Containers API
export const containersApi = {
  async create(container: ContainerCreate): Promise<Container> {
    const response = await fetch(`${API_BASE}/containers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(container),
    })
    return handleResponse<Container>(response)
  },

  async list(): Promise<ContainerWithCount[]> {
    const response = await fetch(`${API_BASE}/containers`)
    return handleResponse<ContainerWithCount[]>(response)
  },

  async get(id: string): Promise<ContainerWithNotes> {
    const response = await fetch(`${API_BASE}/containers/${id}`)
    return handleResponse<ContainerWithNotes>(response)
  },

  async update(id: string, container: ContainerUpdate): Promise<Container> {
    const response = await fetch(`${API_BASE}/containers/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(container),
    })
    return handleResponse<Container>(response)
  },

  async archive(id: string): Promise<Container> {
    const response = await fetch(`${API_BASE}/containers/${id}/archive`, {
      method: 'PATCH',
    })
    return handleResponse<Container>(response)
  },

  async delete(id: string): Promise<void> {
    const response = await fetch(`${API_BASE}/containers/${id}`, {
      method: 'DELETE',
    })
    return handleResponse<void>(response)
  },
}

// Search API
export const searchApi = {
  async inbox(): Promise<Note[]> {
    const response = await fetch(`${API_BASE}/inbox`)
    return handleResponse<Note[]>(response)
  },

  async search(q: string): Promise<Note[]> {
    const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(q)}`)
    return handleResponse<Note[]>(response)
  },

  async recent(limit = 20): Promise<Note[]> {
    const response = await fetch(`${API_BASE}/recent?limit=${limit}`)
    return handleResponse<Note[]>(response)
  },
}
