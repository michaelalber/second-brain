<script setup lang="ts">
import { computed } from 'vue'
import type { Editor } from '@tiptap/core'

const props = defineProps<{
  editor: Editor
}>()

// Reactive state for button active states
const isActive = computed(() => ({
  bold: props.editor.isActive('bold'),
  italic: props.editor.isActive('italic'),
  h1: props.editor.isActive('heading', { level: 1 }),
  h2: props.editor.isActive('heading', { level: 2 }),
  h3: props.editor.isActive('heading', { level: 3 }),
  bulletList: props.editor.isActive('bulletList'),
  orderedList: props.editor.isActive('orderedList'),
  l2Highlight: props.editor.isActive('l2Highlight'),
  l3Highlight: props.editor.isActive('l3Highlight'),
}))

function toggleBold() {
  props.editor.chain().focus().toggleBold().run()
}

function toggleItalic() {
  props.editor.chain().focus().toggleItalic().run()
}

function toggleHeading(level: 1 | 2 | 3) {
  props.editor.chain().focus().toggleHeading({ level }).run()
}

function toggleBulletList() {
  props.editor.chain().focus().toggleBulletList().run()
}

function toggleOrderedList() {
  props.editor.chain().focus().toggleOrderedList().run()
}

function toggleL2Highlight() {
  props.editor.chain().focus().toggleL2Highlight().run()
}

function toggleL3Highlight() {
  props.editor.chain().focus().toggleL3Highlight().run()
}
</script>

<template>
  <div class="flex flex-wrap items-center gap-1 p-2 border-b border-gray-200 bg-gray-50 rounded-t-lg">
    <!-- Formatting buttons -->
    <div class="flex items-center gap-1 pr-2 border-r border-gray-300">
      <button
        data-testid="btn-bold"
        type="button"
        class="toolbar-btn"
        :class="{ 'is-active': isActive.bold }"
        title="Bold (Ctrl+B)"
        @click="toggleBold"
      >
        <span class="font-bold">B</span>
      </button>
      <button
        data-testid="btn-italic"
        type="button"
        class="toolbar-btn"
        :class="{ 'is-active': isActive.italic }"
        title="Italic (Ctrl+I)"
        @click="toggleItalic"
      >
        <span class="italic">I</span>
      </button>
    </div>

    <!-- Heading buttons -->
    <div class="flex items-center gap-1 pr-2 border-r border-gray-300">
      <button
        data-testid="btn-h1"
        type="button"
        class="toolbar-btn"
        :class="{ 'is-active': isActive.h1 }"
        title="Heading 1"
        @click="toggleHeading(1)"
      >
        H1
      </button>
      <button
        data-testid="btn-h2"
        type="button"
        class="toolbar-btn"
        :class="{ 'is-active': isActive.h2 }"
        title="Heading 2"
        @click="toggleHeading(2)"
      >
        H2
      </button>
      <button
        data-testid="btn-h3"
        type="button"
        class="toolbar-btn"
        :class="{ 'is-active': isActive.h3 }"
        title="Heading 3"
        @click="toggleHeading(3)"
      >
        H3
      </button>
    </div>

    <!-- List buttons -->
    <div class="flex items-center gap-1 pr-2 border-r border-gray-300">
      <button
        data-testid="btn-bullet-list"
        type="button"
        class="toolbar-btn"
        :class="{ 'is-active': isActive.bulletList }"
        title="Bullet List"
        @click="toggleBulletList"
      >
        <span class="text-lg leading-none">&bull;</span>
      </button>
      <button
        data-testid="btn-ordered-list"
        type="button"
        class="toolbar-btn"
        :class="{ 'is-active': isActive.orderedList }"
        title="Numbered List"
        @click="toggleOrderedList"
      >
        <span class="text-sm">1.</span>
      </button>
    </div>

    <!-- Progressive Summarization buttons -->
    <div class="flex items-center gap-1">
      <button
        data-testid="btn-l2"
        type="button"
        class="toolbar-btn l2-btn"
        :class="{ 'is-active': isActive.l2Highlight }"
        title="L2: Bold Passage (mark important sections)"
        @click="toggleL2Highlight"
      >
        L2
      </button>
      <button
        data-testid="btn-l3"
        type="button"
        class="toolbar-btn l3-btn"
        :class="{ 'is-active': isActive.l3Highlight }"
        title="L3: Key Insight (highlight within bold)"
        @click="toggleL3Highlight"
      >
        L3
      </button>
    </div>
  </div>
</template>

<style scoped>
.toolbar-btn {
  @apply px-2 py-1 rounded text-sm text-gray-600 hover:bg-gray-200 transition-colors min-w-[32px] h-8 flex items-center justify-center;
}

.toolbar-btn.is-active {
  @apply bg-gray-300 text-gray-900;
}

.l2-btn {
  @apply bg-amber-50 hover:bg-amber-100 text-amber-800;
}

.l2-btn.is-active {
  @apply bg-amber-200 text-amber-900;
}

.l3-btn {
  @apply bg-yellow-100 hover:bg-yellow-200 text-yellow-800;
}

.l3-btn.is-active {
  @apply bg-yellow-300 text-yellow-900;
}
</style>
