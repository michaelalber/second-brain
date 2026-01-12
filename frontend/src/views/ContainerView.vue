<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useContainersStore } from '@/stores/containers'
import NoteCard from '@/components/NoteCard.vue'

const props = defineProps<{
  id: string
}>()

const containersStore = useContainersStore()
const { currentContainer, loading, error } = storeToRefs(containersStore)

const typeColors = {
  project: 'bg-blue-100 text-blue-800',
  area: 'bg-green-100 text-green-800',
  resource: 'bg-yellow-100 text-yellow-800',
  archive: 'bg-gray-100 text-gray-800',
}

onMounted(() => {
  containersStore.fetchContainer(props.id)
})

watch(
  () => props.id,
  (newId) => {
    containersStore.fetchContainer(newId)
  }
)
</script>

<template>
  <div>
    <div v-if="loading" class="text-gray-500">Loading...</div>

    <div v-else-if="error" class="text-red-500">{{ error }}</div>

    <template v-else-if="currentContainer">
      <header class="mb-8">
        <div class="flex items-start justify-between gap-4 mb-2">
          <h1 class="text-2xl font-bold text-gray-900">
            {{ currentContainer.name }}
          </h1>
          <span
            :class="[
              'px-3 py-1 text-sm font-medium rounded-full uppercase',
              typeColors[currentContainer.type],
            ]"
          >
            {{ currentContainer.type }}
          </span>
        </div>
        <p v-if="currentContainer.description" class="text-gray-600">
          {{ currentContainer.description }}
        </p>
      </header>

      <!-- Notes -->
      <section>
        <h2 class="text-lg font-semibold text-gray-800 mb-4">
          Notes ({{ currentContainer.notes?.length || 0 }})
        </h2>

        <div
          v-if="!currentContainer.notes || currentContainer.notes.length === 0"
          class="text-gray-500"
        >
          No notes in this container yet.
        </div>

        <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <NoteCard
            v-for="note in currentContainer.notes"
            :key="note.id"
            :note="note"
          />
        </div>
      </section>
    </template>
  </div>
</template>
