<script setup lang="ts">
import { onMounted, onBeforeUnmount, watch, shallowRef } from 'vue'
import { Editor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import EditorToolbar from './EditorToolbar.vue'
import { L2Highlight } from '@/editor/extensions/L2Highlight'
import { L3Highlight } from '@/editor/extensions/L3Highlight'

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

const editor = shallowRef<Editor | null>(null)

onMounted(() => {
  editor.value = new Editor({
    extensions: [StarterKit, L2Highlight, L3Highlight],
    content: props.modelValue,
    editable: !props.readonly,
    onUpdate: ({ editor }) => {
      emit('update:modelValue', editor.getHTML())
    },
  })
})

onBeforeUnmount(() => {
  editor.value?.destroy()
})

// Watch for external content changes
watch(
  () => props.modelValue,
  (newContent) => {
    if (editor.value && editor.value.getHTML() !== newContent) {
      editor.value.commands.setContent(newContent, { emitUpdate: false })
    }
  }
)

// Watch for readonly changes
watch(
  () => props.readonly,
  (readonly) => {
    editor.value?.setEditable(!readonly)
  }
)

// Expose editor for parent components if needed
defineExpose({
  editor,
  getHTML: () => editor.value?.getHTML() ?? '',
  getText: () => editor.value?.getText() ?? '',
})
</script>

<template>
  <div class="rich-editor border border-gray-300 rounded-lg overflow-hidden">
    <EditorToolbar v-if="editor && !readonly" :editor="editor" />
    <EditorContent
      v-if="editor"
      :editor="editor"
      class="prose prose-sm max-w-none p-4 min-h-[200px] focus:outline-none"
    />
  </div>
</template>

<style>
/* Tiptap editor styles */
.rich-editor .ProseMirror {
  outline: none;
  min-height: 200px;
}

.rich-editor .ProseMirror p {
  margin: 0.5em 0;
}

.rich-editor .ProseMirror h1 {
  font-size: 1.5em;
  font-weight: bold;
  margin: 0.5em 0;
}

.rich-editor .ProseMirror h2 {
  font-size: 1.25em;
  font-weight: bold;
  margin: 0.5em 0;
}

.rich-editor .ProseMirror h3 {
  font-size: 1.1em;
  font-weight: bold;
  margin: 0.5em 0;
}

.rich-editor .ProseMirror ul,
.rich-editor .ProseMirror ol {
  padding-left: 1.5em;
  margin: 0.5em 0;
}

.rich-editor .ProseMirror li {
  margin: 0.25em 0;
}

/* L2 Highlight - Bold passage with subtle background */
.rich-editor .ProseMirror .l2-highlight,
.rich-editor .ProseMirror mark[data-l2-highlight] {
  font-weight: bold;
  background-color: rgb(254 243 199); /* amber-100 */
  padding: 0.1em 0.2em;
  border-radius: 0.2em;
}

/* L3 Highlight - Key insight with yellow highlight */
.rich-editor .ProseMirror .l3-highlight,
.rich-editor .ProseMirror mark[data-l3-highlight] {
  font-weight: bold;
  background-color: rgb(254 240 138); /* yellow-200 */
  padding: 0.1em 0.2em;
  border-radius: 0.2em;
}

/* When both L2 and L3 are applied, L3 takes visual precedence */
.rich-editor .ProseMirror mark[data-l2-highlight] mark[data-l3-highlight],
.rich-editor .ProseMirror mark[data-l3-highlight] {
  background-color: rgb(254 240 138); /* yellow-200 */
}
</style>
