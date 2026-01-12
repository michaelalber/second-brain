import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useNotesStore } from '../notes'
import * as client from '@/api/client'

// Mock the API client
vi.mock('@/api/client', () => ({
  notesApi: {
    create: vi.fn(),
    list: vi.fn(),
    get: vi.fn(),
    update: vi.fn(),
    move: vi.fn(),
    updateHighlights: vi.fn(),
    delete: vi.fn(),
  },
  searchApi: {
    inbox: vi.fn(),
    search: vi.fn(),
    recent: vi.fn(),
  },
}))

const mockNote = {
  id: 'note-1',
  title: 'Test Note',
  content: 'Test content',
  highlights: {},
  code_stage: 'capture' as const,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  captured_at: '2024-01-01T00:00:00Z',
}

describe('Notes Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('adds note to inbox with capture stage via quickCapture', async () => {
    const store = useNotesStore()

    vi.mocked(client.notesApi.create).mockResolvedValue(mockNote)

    await store.quickCapture({ title: 'New idea', content: 'Details...' })

    expect(client.notesApi.create).toHaveBeenCalledWith({
      title: 'New idea',
      content: 'Details...',
    })
    expect(store.notes).toHaveLength(1)
    expect(store.notes[0].code_stage).toBe('capture')
  })

  it('inbox getter returns only capture stage notes without container', () => {
    const store = useNotesStore()

    store.notes = [
      { ...mockNote, id: '1', code_stage: 'capture', container_id: null },
      { ...mockNote, id: '2', code_stage: 'organize', container_id: 'container-1' },
      { ...mockNote, id: '3', code_stage: 'capture', container_id: 'container-2' },
    ]

    expect(store.inbox).toHaveLength(1)
    expect(store.inbox[0].id).toBe('1')
  })

  it('moves note and updates its container and stage', async () => {
    const store = useNotesStore()
    const movedNote = {
      ...mockNote,
      container_id: 'container-1',
      code_stage: 'organize' as const,
    }

    store.notes = [mockNote]

    vi.mocked(client.notesApi.move).mockResolvedValue(movedNote)

    await store.moveToContainer('note-1', 'container-1')

    expect(client.notesApi.move).toHaveBeenCalledWith('note-1', {
      container_id: 'container-1',
    })
    expect(store.notes[0].container_id).toBe('container-1')
    expect(store.notes[0].code_stage).toBe('organize')
  })

  it('fetches inbox notes', async () => {
    const store = useNotesStore()

    vi.mocked(client.searchApi.inbox).mockResolvedValue([mockNote])

    await store.fetchInbox()

    expect(client.searchApi.inbox).toHaveBeenCalled()
    expect(store.notes).toHaveLength(1)
  })

  it('searches notes', async () => {
    const store = useNotesStore()

    vi.mocked(client.searchApi.search).mockResolvedValue([mockNote])

    await store.searchNotes('test')

    expect(client.searchApi.search).toHaveBeenCalledWith('test')
    expect(store.notes).toHaveLength(1)
  })

  it('deletes note and removes from list', async () => {
    const store = useNotesStore()
    store.notes = [mockNote]

    vi.mocked(client.notesApi.delete).mockResolvedValue(undefined)

    await store.deleteNote('note-1')

    expect(client.notesApi.delete).toHaveBeenCalledWith('note-1')
    expect(store.notes).toHaveLength(0)
  })

  it('updates highlights and changes stage to distill', async () => {
    const store = useNotesStore()
    const updatedNote = {
      ...mockNote,
      highlights: { highlights: [{ start: 0, end: 10, layer: 2 }] },
      code_stage: 'distill' as const,
    }

    store.notes = [mockNote]

    vi.mocked(client.notesApi.updateHighlights).mockResolvedValue(updatedNote)

    await store.updateHighlights('note-1', {
      highlights: [{ start: 0, end: 10, layer: 2 }],
    })

    expect(store.notes[0].code_stage).toBe('distill')
  })
})
