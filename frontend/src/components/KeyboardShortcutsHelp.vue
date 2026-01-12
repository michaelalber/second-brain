<script setup lang="ts">
import type { KeyboardShortcut } from '@/composables/useKeyboardShortcuts'

defineProps<{
  shortcuts: KeyboardShortcut[]
}>()

const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <div
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    @click.self="emit('close')"
    @keydown.escape="emit('close')"
  >
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold text-gray-900">Keyboard Shortcuts</h2>
        <button @click="emit('close')" class="text-gray-400 hover:text-gray-600">
          <span class="text-2xl">&times;</span>
        </button>
      </div>

      <div class="space-y-2">
        <div
          v-for="shortcut in shortcuts"
          :key="shortcut.key"
          class="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
        >
          <span class="text-gray-700">{{ shortcut.description }}</span>
          <kbd
            class="px-2 py-1 bg-gray-100 border border-gray-300 rounded text-sm font-mono text-gray-700"
          >
            {{ shortcut.key }}
          </kbd>
        </div>
      </div>

      <div class="mt-4 pt-4 border-t border-gray-200 text-sm text-gray-500">
        Press <kbd class="px-1 bg-gray-100 border border-gray-200 rounded text-xs">?</kbd> anywhere
        to toggle this help
      </div>
    </div>
  </div>
</template>
