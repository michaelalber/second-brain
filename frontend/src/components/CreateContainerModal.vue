<script setup lang="ts">
import { ref } from 'vue'
import { useContainersStore } from '@/stores/containers'
import type { ContainerType } from '@/types'

const emit = defineEmits<{
  close: []
}>()

const containersStore = useContainersStore()

const name = ref('')
const type = ref<ContainerType>('project')
const description = ref('')
const isSubmitting = ref(false)
const error = ref('')

const containerTypes: { value: ContainerType; label: string; description: string }[] = [
  { value: 'project', label: 'Project', description: 'Short-term efforts with deadlines' },
  { value: 'area', label: 'Area', description: 'Ongoing responsibilities' },
  { value: 'resource', label: 'Resource', description: 'Topics of interest' },
]

async function handleSubmit() {
  if (!name.value.trim()) {
    error.value = 'Name is required'
    return
  }

  isSubmitting.value = true
  error.value = ''

  try {
    await containersStore.createContainer({
      name: name.value.trim(),
      type: type.value,
      description: description.value.trim() || undefined,
    })
    emit('close')
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to create container'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="emit('close')">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold text-gray-900">Create Container</h2>
        <button @click="emit('close')" class="text-gray-400 hover:text-gray-600">
          <span class="text-2xl">&times;</span>
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
          <input
            v-model="name"
            type="text"
            placeholder="Container name"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            autofocus
          />
        </div>

        <!-- Type -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Type</label>
          <div class="space-y-2">
            <label
              v-for="ct in containerTypes"
              :key="ct.value"
              class="flex items-start gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50"
              :class="type === ct.value ? 'border-blue-500 bg-blue-50' : 'border-gray-200'"
            >
              <input
                v-model="type"
                type="radio"
                :value="ct.value"
                class="mt-1"
              />
              <div>
                <div class="font-medium text-gray-900">{{ ct.label }}</div>
                <div class="text-sm text-gray-500">{{ ct.description }}</div>
              </div>
            </label>
          </div>
        </div>

        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Description <span class="text-gray-400">(optional)</span>
          </label>
          <textarea
            v-model="description"
            placeholder="What is this container for?"
            rows="2"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          ></textarea>
        </div>

        <!-- Error -->
        <div v-if="error" class="text-red-500 text-sm">{{ error }}</div>

        <!-- Actions -->
        <div class="flex justify-end gap-3 pt-2">
          <button
            type="button"
            @click="emit('close')"
            class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="isSubmitting || !name.trim()"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isSubmitting ? 'Creating...' : 'Create' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
