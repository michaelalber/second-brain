<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useNotesStore } from '@/stores/notes'
import NoteCard from '@/components/NoteCard.vue'

const notesStore = useNotesStore()
const { notes, loading, error } = storeToRefs(notesStore)

const newTitle = ref('')
const newContent = ref('')
const sourceUrl = ref('')
const sourceType = ref('')
const showAdvanced = ref(false)
const isCapturing = ref(false)

const sourceTypes = [
  { value: '', label: 'Select type...' },
  { value: 'article', label: 'Article' },
  { value: 'book', label: 'Book' },
  { value: 'podcast', label: 'Podcast' },
  { value: 'video', label: 'Video' },
  { value: 'thought', label: 'Thought' },
  { value: 'meeting', label: 'Meeting' },
  { value: 'conversation', label: 'Conversation' },
]

onMounted(() => {
  notesStore.fetchInbox()
})

async function handleCapture() {
  if (!newTitle.value.trim() || !newContent.value.trim()) return

  isCapturing.value = true
  try {
    await notesStore.quickCapture({
      title: newTitle.value.trim(),
      content: newContent.value.trim(),
      source_url: sourceUrl.value.trim() || undefined,
      source_type: sourceType.value || undefined,
    })
    // Reset form
    newTitle.value = ''
    newContent.value = ''
    sourceUrl.value = ''
    sourceType.value = ''
    showAdvanced.value = false
  } finally {
    isCapturing.value = false
  }
}
</script>

<template>
  <div>
    <header class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Inbox</h1>
      <p class="text-gray-600">Capture new ideas quickly</p>
    </header>

    <!-- Quick Capture Form -->
    <section class="mb-8 p-4 bg-white rounded-lg border border-gray-200">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">Quick Capture</h2>
      <form @submit.prevent="handleCapture" class="space-y-4">
        <div>
          <input
            v-model="newTitle"
            type="text"
            placeholder="Title"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <textarea
            v-model="newContent"
            placeholder="What's on your mind?"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          ></textarea>
        </div>

        <!-- Advanced Options Toggle -->
        <button
          type="button"
          @click="showAdvanced = !showAdvanced"
          class="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
        >
          <span>{{ showAdvanced ? '−' : '+' }}</span>
          <span>{{ showAdvanced ? 'Hide' : 'Show' }} source options</span>
        </button>

        <!-- Advanced Options -->
        <div v-if="showAdvanced" class="space-y-3 p-3 bg-gray-50 rounded-lg">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Source URL</label>
            <input
              v-model="sourceUrl"
              type="url"
              placeholder="https://..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Source Type</label>
            <select
              v-model="sourceType"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option v-for="st in sourceTypes" :key="st.value" :value="st.value">
                {{ st.label }}
              </option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          :disabled="isCapturing || !newTitle.trim() || !newContent.trim()"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isCapturing ? 'Capturing...' : 'Capture' }}
        </button>
      </form>
    </section>

    <!-- Inbox Notes -->
    <section>
      <h2 class="text-lg font-semibold text-gray-800 mb-4">
        Inbox Items ({{ notes.length }})
      </h2>

      <div v-if="loading" class="text-gray-500">Loading...</div>

      <div v-else-if="error" class="text-red-500">{{ error }}</div>

      <div v-else-if="notes.length === 0" class="text-gray-500">
        Your inbox is empty. Capture something above!
      </div>

      <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <NoteCard v-for="note in notes" :key="note.id" :note="note" />
      </div>
    </section>
  </div>
</template>
