<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useNotesStore } from '@/stores/notes'
import { useContainersStore } from '@/stores/containers'

const props = defineProps<{
  id: string
}>()

const router = useRouter()
const notesStore = useNotesStore()
const containersStore = useContainersStore()

const { currentNote, loading, error } = storeToRefs(notesStore)
const { containers } = storeToRefs(containersStore)

const stageColors = {
  capture: 'bg-yellow-100 text-yellow-800',
  organize: 'bg-blue-100 text-blue-800',
  distill: 'bg-purple-100 text-purple-800',
  express: 'bg-green-100 text-green-800',
}

onMounted(() => {
  notesStore.fetchNote(props.id)
  containersStore.fetchContainers()
})

watch(
  () => props.id,
  (newId) => {
    notesStore.fetchNote(newId)
  }
)

async function handleMove(containerId: string) {
  await notesStore.moveToContainer(props.id, containerId)
}

async function handleDelete() {
  if (confirm('Are you sure you want to delete this note?')) {
    await notesStore.deleteNote(props.id)
    router.push('/inbox')
  }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<template>
  <div>
    <div v-if="loading" class="text-gray-500">Loading...</div>

    <div v-else-if="error" class="text-red-500">{{ error }}</div>

    <template v-else-if="currentNote">
      <header class="mb-6">
        <div class="flex items-start justify-between gap-4 mb-4">
          <h1 class="text-2xl font-bold text-gray-900">
            {{ currentNote.title }}
          </h1>
          <span
            :class="[
              'px-3 py-1 text-sm font-medium rounded-full',
              stageColors[currentNote.code_stage],
            ]"
          >
            {{ currentNote.code_stage }}
          </span>
        </div>

        <div class="flex items-center gap-4 text-sm text-gray-500">
          <span>Captured: {{ formatDate(currentNote.captured_at) }}</span>
          <span v-if="currentNote.source_type" class="italic">
            Source: {{ currentNote.source_type }}
          </span>
          <a
            v-if="currentNote.source_url"
            :href="currentNote.source_url"
            target="_blank"
            class="text-blue-600 hover:underline"
          >
            View source
          </a>
        </div>
      </header>

      <!-- Content -->
      <article class="prose max-w-none mb-8 p-6 bg-white rounded-lg border border-gray-200">
        <p class="whitespace-pre-wrap">{{ currentNote.content }}</p>
      </article>

      <!-- Executive Summary -->
      <section
        v-if="currentNote.executive_summary"
        class="mb-8 p-4 bg-purple-50 rounded-lg border border-purple-200"
      >
        <h2 class="text-lg font-semibold text-purple-800 mb-2">
          Executive Summary (L4)
        </h2>
        <p class="text-purple-900">{{ currentNote.executive_summary }}</p>
      </section>

      <!-- Actions -->
      <section class="p-4 bg-gray-50 rounded-lg border border-gray-200">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Actions</h2>

        <!-- Move to Container -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Move to Container
          </label>
          <select
            :value="currentNote.container_id || ''"
            @change="(e) => handleMove((e.target as HTMLSelectElement).value)"
            class="w-full max-w-xs px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">No container (Inbox)</option>
            <option
              v-for="container in containers"
              :key="container.id"
              :value="container.id"
            >
              {{ container.type.toUpperCase() }}: {{ container.name }}
            </option>
          </select>
        </div>

        <!-- Delete -->
        <button
          @click="handleDelete"
          class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Delete Note
        </button>
      </section>
    </template>
  </div>
</template>
