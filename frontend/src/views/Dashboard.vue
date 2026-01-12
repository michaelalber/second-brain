<script setup lang="ts">
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useNotesStore } from '@/stores/notes'
import NoteCard from '@/components/NoteCard.vue'

const notesStore = useNotesStore()
const { notes, loading, error } = storeToRefs(notesStore)

onMounted(() => {
  notesStore.fetchRecent(10)
})
</script>

<template>
  <div>
    <header class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
      <p class="text-gray-600">Your recent notes and activity</p>
    </header>

    <section>
      <h2 class="text-lg font-semibold text-gray-800 mb-4">Recent Notes</h2>

      <div v-if="loading" class="text-gray-500">Loading...</div>

      <div v-else-if="error" class="text-red-500">{{ error }}</div>

      <div v-else-if="notes.length === 0" class="text-gray-500">
        No notes yet. Start by capturing something in the Inbox!
      </div>

      <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <NoteCard v-for="note in notes" :key="note.id" :note="note" />
      </div>
    </section>
  </div>
</template>
