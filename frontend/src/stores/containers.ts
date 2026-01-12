import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Container,
  ContainerCreate,
  ContainerUpdate,
  ContainerWithCount,
  ContainerWithNotes,
  ContainerType,
} from '@/types'
import { containersApi } from '@/api/client'

export const useContainersStore = defineStore('containers', () => {
  // State
  const containers = ref<ContainerWithCount[]>([])
  const currentContainer = ref<ContainerWithNotes | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const projects = computed(() =>
    containers.value.filter((c) => c.type === 'project' && c.is_active)
  )

  const areas = computed(() =>
    containers.value.filter((c) => c.type === 'area' && c.is_active)
  )

  const resources = computed(() =>
    containers.value.filter((c) => c.type === 'resource' && c.is_active)
  )

  const archives = computed(() =>
    containers.value.filter((c) => c.type === 'archive' || !c.is_active)
  )

  const byType = computed(() => (type: ContainerType) =>
    containers.value.filter((c) => c.type === type)
  )

  const totalNoteCount = computed(() =>
    containers.value.reduce((sum, c) => sum + c.note_count, 0)
  )

  // Actions
  async function fetchContainers() {
    loading.value = true
    error.value = null
    try {
      containers.value = await containersApi.list()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch containers'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchContainer(id: string) {
    loading.value = true
    error.value = null
    try {
      currentContainer.value = await containersApi.get(id)
      return currentContainer.value
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch container'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createContainer(containerData: ContainerCreate) {
    loading.value = true
    error.value = null
    try {
      const container = await containersApi.create(containerData)
      // Refetch to get the count
      await fetchContainers()
      return container
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to create container'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateContainer(id: string, containerData: ContainerUpdate) {
    loading.value = true
    error.value = null
    try {
      const updated = await containersApi.update(id, containerData)
      const index = containers.value.findIndex((c) => c.id === id)
      if (index !== -1) {
        containers.value[index] = {
          ...containers.value[index],
          ...updated,
        }
      }
      if (currentContainer.value?.id === id) {
        currentContainer.value = {
          ...currentContainer.value,
          ...updated,
        }
      }
      return updated
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update container'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function archiveContainer(id: string) {
    loading.value = true
    error.value = null
    try {
      const updated = await containersApi.archive(id)
      const index = containers.value.findIndex((c) => c.id === id)
      if (index !== -1) {
        containers.value[index] = {
          ...containers.value[index],
          ...updated,
        }
      }
      if (currentContainer.value?.id === id) {
        currentContainer.value = {
          ...currentContainer.value,
          ...updated,
        }
      }
      return updated
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to archive container'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteContainer(id: string) {
    loading.value = true
    error.value = null
    try {
      await containersApi.delete(id)
      containers.value = containers.value.filter((c) => c.id !== id)
      if (currentContainer.value?.id === id) {
        currentContainer.value = null
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete container'
      throw e
    } finally {
      loading.value = false
    }
  }

  function clearCurrentContainer() {
    currentContainer.value = null
  }

  return {
    // State
    containers,
    currentContainer,
    loading,
    error,
    // Getters
    projects,
    areas,
    resources,
    archives,
    byType,
    totalNoteCount,
    // Actions
    fetchContainers,
    fetchContainer,
    createContainer,
    updateContainer,
    archiveContainer,
    deleteContainer,
    clearCurrentContainer,
  }
})
