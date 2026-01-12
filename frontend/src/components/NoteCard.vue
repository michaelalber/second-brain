<script setup lang="ts">
import type { Note } from '@/types'

defineProps<{
  note: Note
}>()

const stageColors = {
  capture: 'bg-yellow-100 text-yellow-800',
  organize: 'bg-blue-100 text-blue-800',
  distill: 'bg-purple-100 text-purple-800',
  express: 'bg-green-100 text-green-800',
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}

function truncate(text: string, length: number): string {
  if (text.length <= length) return text
  return text.slice(0, length) + '...'
}
</script>

<template>
  <router-link
    :to="`/notes/${note.id}`"
    class="block p-4 bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-sm transition-all"
  >
    <div class="flex items-start justify-between gap-2 mb-2">
      <h3 class="font-medium text-gray-900 line-clamp-1">
        {{ note.title }}
      </h3>
      <span
        :class="[
          'px-2 py-0.5 text-xs font-medium rounded-full',
          stageColors[note.code_stage],
        ]"
      >
        {{ note.code_stage }}
      </span>
    </div>

    <p class="text-sm text-gray-600 mb-3 line-clamp-2">
      {{ truncate(note.content, 150) }}
    </p>

    <div class="flex items-center justify-between text-xs text-gray-400">
      <span>{{ formatDate(note.captured_at) }}</span>
      <span v-if="note.source_type" class="italic">
        {{ note.source_type }}
      </span>
    </div>
  </router-link>
</template>
