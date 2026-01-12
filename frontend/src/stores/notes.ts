import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Note, NoteCreate, NoteUpdate, NoteHighlightsUpdate } from '@/types'
import { notesApi, searchApi } from '@/api/client'

export const useNotesStore = defineStore('notes', () => {
  // State
  const notes = ref<Note[]>([])
  const currentNote = ref<Note | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const inbox = computed(() =>
    notes.value.filter(
      (note) => note.code_stage === 'capture' && !note.container_id
    )
  )

  const byContainer = computed(() => (containerId: string) =>
    notes.value.filter((note) => note.container_id === containerId)
  )

  const byStage = computed(() => (stage: string) =>
    notes.value.filter((note) => note.code_stage === stage)
  )

  // Actions
  async function fetchNotes(params?: {
    container_id?: string
    stage?: string
    q?: string
  }) {
    loading.value = true
    error.value = null
    try {
      notes.value = await notesApi.list(params)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch notes'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchInbox() {
    loading.value = true
    error.value = null
    try {
      notes.value = await searchApi.inbox()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch inbox'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchRecent(limit = 20) {
    loading.value = true
    error.value = null
    try {
      notes.value = await searchApi.recent(limit)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch recent'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchNote(id: string) {
    loading.value = true
    error.value = null
    try {
      currentNote.value = await notesApi.get(id)
      return currentNote.value
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch note'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function quickCapture(noteData: NoteCreate) {
    loading.value = true
    error.value = null
    try {
      const note = await notesApi.create(noteData)
      notes.value.unshift(note)
      return note
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to create note'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateNote(id: string, noteData: NoteUpdate) {
    loading.value = true
    error.value = null
    try {
      const updated = await notesApi.update(id, noteData)
      const index = notes.value.findIndex((n) => n.id === id)
      if (index !== -1) {
        notes.value[index] = updated
      }
      if (currentNote.value?.id === id) {
        currentNote.value = updated
      }
      return updated
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update note'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function moveToContainer(noteId: string, containerId: string) {
    loading.value = true
    error.value = null
    try {
      const updated = await notesApi.move(noteId, { container_id: containerId })
      const index = notes.value.findIndex((n) => n.id === noteId)
      if (index !== -1) {
        notes.value[index] = updated
      }
      if (currentNote.value?.id === noteId) {
        currentNote.value = updated
      }
      return updated
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to move note'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateHighlights(noteId: string, highlights: NoteHighlightsUpdate) {
    loading.value = true
    error.value = null
    try {
      const updated = await notesApi.updateHighlights(noteId, highlights)
      const index = notes.value.findIndex((n) => n.id === noteId)
      if (index !== -1) {
        notes.value[index] = updated
      }
      if (currentNote.value?.id === noteId) {
        currentNote.value = updated
      }
      return updated
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update highlights'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteNote(id: string) {
    loading.value = true
    error.value = null
    try {
      await notesApi.delete(id)
      notes.value = notes.value.filter((n) => n.id !== id)
      if (currentNote.value?.id === id) {
        currentNote.value = null
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete note'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function searchNotes(query: string) {
    loading.value = true
    error.value = null
    try {
      notes.value = await searchApi.search(query)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to search notes'
      throw e
    } finally {
      loading.value = false
    }
  }

  function clearCurrentNote() {
    currentNote.value = null
  }

  return {
    // State
    notes,
    currentNote,
    loading,
    error,
    // Getters
    inbox,
    byContainer,
    byStage,
    // Actions
    fetchNotes,
    fetchInbox,
    fetchRecent,
    fetchNote,
    quickCapture,
    updateNote,
    moveToContainer,
    updateHighlights,
    deleteNote,
    searchNotes,
    clearCurrentNote,
  }
})
