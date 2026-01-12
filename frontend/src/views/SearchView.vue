<script setup lang="ts">
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useNotesStore } from '@/stores/notes'
import NoteCard from '@/components/NoteCard.vue'

const notesStore = useNotesStore()
const { notes, loading, error } = storeToRefs(notesStore)

const searchQuery = ref('')
const hasSearched = ref(false)

async function handleSearch() {
  if (!searchQuery.value.trim()) return

  hasSearched.value = true
  await notesStore.searchNotes(searchQuery.value.trim())
}
</script>

<template>
  <div>
    <header class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Search</h1>
      <p class="text-gray-600">Find notes across your second brain</p>
    </header>

    <!-- Search Form -->
    <section class="mb-8">
      <form @submit.prevent="handleSearch" class="flex gap-2">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search notes..."
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          :disabled="loading || !searchQuery.trim()"
          class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ loading ? 'Searching...' : 'Search' }}
        </button>
      </form>
    </section>

    <!-- Results -->
    <section>
      <div v-if="loading" class="text-gray-500">Searching...</div>

      <div v-else-if="error" class="text-red-500">{{ error }}</div>

      <template v-else-if="hasSearched">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">
          Results ({{ notes.length }})
        </h2>

        <div v-if="notes.length === 0" class="text-gray-500">
          No notes found matching "{{ searchQuery }}"
        </div>

        <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <NoteCard v-for="note in notes" :key="note.id" :note="note" />
        </div>
      </template>

      <div v-else class="text-gray-500">
        Enter a search term to find notes
      </div>
    </section>
  </div>
</template>
