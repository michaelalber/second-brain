<script setup lang="ts">
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useContainersStore } from '@/stores/containers'
import { useNotesStore } from '@/stores/notes'
import type { Container } from '@/types'

const props = defineProps<{
  noteId: string
  currentContainerId: string | null
}>()

const emit = defineEmits<{
  close: []
  moved: []
}>()

const containersStore = useContainersStore()
const notesStore = useNotesStore()
const { projects, areas, resources } = storeToRefs(containersStore)

const selectedContainerId = ref<string | null>(props.currentContainerId)
const isMoving = ref(false)

const containerSections = computed(() => [
  { title: 'Projects', icon: '🎯', items: projects.value, description: 'Short-term efforts with deadlines' },
  { title: 'Areas', icon: '🔄', items: areas.value, description: 'Ongoing responsibilities' },
  { title: 'Resources', icon: '📚', items: resources.value, description: 'Topics of interest' },
])

const hasChanged = computed(() => selectedContainerId.value !== props.currentContainerId)

function selectContainer(container: Container | null) {
  selectedContainerId.value = container?.id ?? null
}

async function handleMove() {
  if (!hasChanged.value) {
    emit('close')
    return
  }

  isMoving.value = true
  try {
    await notesStore.moveToContainer(props.noteId, selectedContainerId.value)
    emit('moved')
    emit('close')
  } finally {
    isMoving.value = false
  }
}
</script>

<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-lg max-h-[80vh] flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-200">
        <h2 class="text-xl font-semibold text-gray-900">Move Note</h2>
        <button @click="emit('close')" class="text-gray-400 hover:text-gray-600">
          <span class="text-2xl">&times;</span>
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-4">
        <!-- Inbox option -->
        <button
          @click="selectContainer(null)"
          class="w-full text-left p-3 rounded-lg border-2 mb-4 transition-colors"
          :class="selectedContainerId === null
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-200 hover:border-gray-300'"
        >
          <div class="flex items-center gap-3">
            <span class="text-xl">📥</span>
            <div>
              <div class="font-medium text-gray-900">Inbox</div>
              <div class="text-sm text-gray-500">Uncategorized captures</div>
            </div>
          </div>
        </button>

        <!-- PARA Sections -->
        <div v-for="section in containerSections" :key="section.title" class="mb-4">
          <div class="flex items-center gap-2 mb-2 px-1">
            <span>{{ section.icon }}</span>
            <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wider">
              {{ section.title }}
            </h3>
            <span class="text-xs text-gray-400">{{ section.description }}</span>
          </div>

          <div v-if="section.items.length === 0" class="px-3 py-2 text-sm text-gray-400 italic">
            No {{ section.title.toLowerCase() }} yet
          </div>

          <div v-else class="space-y-2">
            <button
              v-for="container in section.items"
              :key="container.id"
              @click="selectContainer(container)"
              class="w-full text-left p-3 rounded-lg border-2 transition-colors"
              :class="selectedContainerId === container.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'"
            >
              <div class="flex items-center justify-between">
                <div>
                  <div class="font-medium text-gray-900">{{ container.name }}</div>
                  <div v-if="container.description" class="text-sm text-gray-500 line-clamp-1">
                    {{ container.description }}
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-xs text-gray-400">{{ container.note_count }} notes</span>
                  <span v-if="container.id === currentContainerId" class="text-xs text-blue-600 font-medium">
                    Current
                  </span>
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex justify-end gap-3 p-4 border-t border-gray-200">
        <button
          @click="emit('close')"
          class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
        >
          Cancel
        </button>
        <button
          @click="handleMove"
          :disabled="isMoving || !hasChanged"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isMoving ? 'Moving...' : 'Move Note' }}
        </button>
      </div>
    </div>
  </div>
</template>
