<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    modelValue: string
    readonly?: boolean
  }>(),
  {
    readonly: false,
  }
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const localValue = computed({
  get: () => props.modelValue,
  set: (value: string) => emit('update:modelValue', value),
})

const hasContent = computed(() => props.modelValue.trim().length > 0)
</script>

<template>
  <div class="executive-summary mt-6 border-t border-gray-200 pt-4">
    <div class="flex items-center gap-2 mb-2">
      <span
        class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800"
      >
        L4
      </span>
      <h3 class="text-sm font-semibold text-gray-700">Executive Summary</h3>
    </div>
    <p class="text-xs text-gray-500 mb-2">
      Summarize the key points in your own words. This is the highest level of distillation.
    </p>

    <!-- Edit mode: textarea -->
    <textarea
      v-if="!readonly"
      v-model="localValue"
      rows="4"
      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent resize-y text-sm"
      placeholder="Write your executive summary here..."
    />

    <!-- View mode: display text -->
    <div v-else class="bg-green-50 rounded-lg p-3">
      <p v-if="hasContent" class="text-sm text-gray-800 whitespace-pre-wrap">
        {{ modelValue }}
      </p>
      <p v-else class="text-sm text-gray-400 italic">No executive summary yet.</p>
    </div>
  </div>
</template>
