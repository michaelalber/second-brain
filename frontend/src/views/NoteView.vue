<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useNotesStore } from '@/stores/notes'
import { useContainersStore } from '@/stores/containers'
import MoveNoteModal from '@/components/MoveNoteModal.vue'
import RichEditor from '@/components/RichEditor.vue'
import ExecutiveSummary from '@/components/ExecutiveSummary.vue'

const props = defineProps<{
  id: string
}>()

const router = useRouter()
const notesStore = useNotesStore()
const containersStore = useContainersStore()

const { currentNote, loading, error } = storeToRefs(notesStore)
const { containers } = storeToRefs(containersStore)

// Edit mode state
const isEditing = ref(false)
const editTitle = ref('')
const editContent = ref('')
const editContentHtml = ref('')
const editExecutiveSummary = ref('')
const isSaving = ref(false)
const showMoveModal = ref(false)

const stageColors = {
  capture: 'bg-yellow-100 text-yellow-800',
  organize: 'bg-blue-100 text-blue-800',
  distill: 'bg-purple-100 text-purple-800',
  express: 'bg-green-100 text-green-800',
}

const hasChanges = computed(() => {
  if (!currentNote.value) return false
  return (
    editTitle.value !== currentNote.value.title ||
    editContentHtml.value !== (currentNote.value.content_html || currentNote.value.content) ||
    editExecutiveSummary.value !== (currentNote.value.executive_summary || '')
  )
})


onMounted(() => {
  notesStore.fetchNote(props.id)
  containersStore.fetchContainers()
  document.addEventListener('keydown', handleNoteKeyDown)
})

watch(
  () => props.id,
  (newId) => {
    notesStore.fetchNote(newId)
    isEditing.value = false
  }
)

watch(currentNote, (note) => {
  if (note) {
    editTitle.value = note.title
    editContent.value = note.content
    editContentHtml.value = note.content_html || note.content
    editExecutiveSummary.value = note.executive_summary || ''
  }
})

function startEditing() {
  if (currentNote.value) {
    editTitle.value = currentNote.value.title
    editContent.value = currentNote.value.content
    editContentHtml.value = currentNote.value.content_html || currentNote.value.content
    editExecutiveSummary.value = currentNote.value.executive_summary || ''
    isEditing.value = true
  }
}

function cancelEditing() {
  if (currentNote.value) {
    editTitle.value = currentNote.value.title
    editContent.value = currentNote.value.content
    editContentHtml.value = currentNote.value.content_html || currentNote.value.content
    editExecutiveSummary.value = currentNote.value.executive_summary || ''
  }
  isEditing.value = false
}

// Extract plain text from HTML for storage
function htmlToPlainText(html: string): string {
  const div = document.createElement('div')
  div.innerHTML = html
  return div.textContent || div.innerText || ''
}

async function saveChanges() {
  if (!hasChanges.value) {
    isEditing.value = false
    return
  }

  isSaving.value = true
  try {
    // Extract plain text from HTML for the content field
    const plainTextContent = htmlToPlainText(editContentHtml.value)

    await notesStore.updateNote(props.id, {
      title: editTitle.value,
      content: plainTextContent,
      content_html: editContentHtml.value,
      executive_summary: editExecutiveSummary.value || undefined,
    })
    isEditing.value = false
  } finally {
    isSaving.value = false
  }
}

const currentContainerName = computed(() => {
  if (!currentNote.value?.container_id) return 'Inbox'
  const container = containers.value.find((c) => c.id === currentNote.value!.container_id)
  return container ? `${container.type.toUpperCase()}: ${container.name}` : 'Unknown'
})

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

// Keyboard shortcuts for note editing
function isInputElement(element: EventTarget | null): boolean {
  if (!element) return false
  const tagName = (element as HTMLElement).tagName?.toLowerCase()
  return (
    tagName === 'input' ||
    tagName === 'textarea' ||
    tagName === 'select' ||
    (element as HTMLElement).isContentEditable
  )
}

function handleNoteKeyDown(event: KeyboardEvent) {
  // Ctrl/Cmd + Enter to save
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter' && isEditing.value) {
    event.preventDefault()
    saveChanges()
    return
  }

  // Escape to cancel editing or close modal
  if (event.key === 'Escape') {
    if (showMoveModal.value) {
      showMoveModal.value = false
      return
    }
    if (isEditing.value) {
      cancelEditing()
      return
    }
  }

  // Don't trigger shortcuts when typing
  if (isInputElement(event.target)) return

  // 'e' to start editing
  if (event.key === 'e' && !isEditing.value && currentNote.value) {
    event.preventDefault()
    startEditing()
    return
  }

  // 'm' to open move modal
  if (event.key === 'm' && !isEditing.value && currentNote.value) {
    event.preventDefault()
    showMoveModal.value = true
    return
  }

  // 'd' to delete (with confirmation)
  if (event.key === 'd' && !isEditing.value && currentNote.value) {
    event.preventDefault()
    handleDelete()
    return
  }
}

onUnmounted(() => {
  document.removeEventListener('keydown', handleNoteKeyDown)
})
</script>

<template>
  <div>
    <div v-if="loading" class="text-gray-500">Loading...</div>

    <div v-else-if="error" class="text-red-500">{{ error }}</div>

    <template v-else-if="currentNote">
      <!-- Header -->
      <header class="mb-6">
        <div class="flex items-start justify-between gap-4 mb-4">
          <!-- Title (editable or display) -->
          <div class="flex-1">
            <input
              v-if="isEditing"
              v-model="editTitle"
              type="text"
              class="w-full text-2xl font-bold text-gray-900 px-2 py-1 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <h1 v-else class="text-2xl font-bold text-gray-900">
              {{ currentNote.title }}
            </h1>
          </div>
          <span
            :class="[
              'px-3 py-1 text-sm font-medium rounded-full shrink-0',
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

      <!-- Content - Rich Editor -->
      <article class="mb-8">
        <RichEditor
          v-model="editContentHtml"
          :readonly="!isEditing"
          class="bg-white"
        />
      </article>

      <!-- Executive Summary (L4) -->
      <ExecutiveSummary
        v-model="editExecutiveSummary"
        :readonly="!isEditing"
        class="mb-8"
      />

      <!-- Edit Actions -->
      <div class="mb-8 flex gap-2">
        <template v-if="isEditing">
          <button
            @click="saveChanges"
            :disabled="isSaving || !hasChanges"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {{ isSaving ? 'Saving...' : 'Save Changes' }}
          </button>
          <button
            @click="cancelEditing"
            :disabled="isSaving"
            class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
          >
            Cancel
          </button>
        </template>
        <button
          v-else
          @click="startEditing"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
        >
          Edit Note
        </button>
      </div>

      <!-- Actions -->
      <section class="p-4 bg-gray-50 rounded-lg border border-gray-200">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Actions</h2>

        <!-- Move to Container -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2"> Location </label>
          <div class="flex items-center gap-3">
            <span class="text-gray-900">{{ currentContainerName }}</span>
            <button
              @click="showMoveModal = true"
              class="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              Move
            </button>
          </div>
        </div>

        <!-- Delete -->
        <button
          @click="handleDelete"
          class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Delete Note
        </button>
      </section>

      <!-- Move Note Modal -->
      <MoveNoteModal
        v-if="showMoveModal"
        :note-id="props.id"
        :current-container-id="currentNote.container_id ?? null"
        @close="showMoveModal = false"
        @moved="notesStore.fetchNote(props.id)"
      />
    </template>
  </div>
</template>
