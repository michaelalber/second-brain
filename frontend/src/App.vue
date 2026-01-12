<script setup lang="ts">
import ParaSidebar from './components/ParaSidebar.vue'
import KeyboardShortcutsHelp from './components/KeyboardShortcutsHelp.vue'
import { useKeyboardShortcuts } from './composables/useKeyboardShortcuts'

const { shortcuts, showHelp } = useKeyboardShortcuts()
</script>

<template>
  <div class="flex min-h-screen bg-gray-50">
    <ParaSidebar />
    <main class="flex-1 p-6 overflow-y-auto">
      <router-view />
    </main>

    <!-- Keyboard Shortcuts Help -->
    <KeyboardShortcutsHelp
      v-if="showHelp"
      :shortcuts="shortcuts"
      @close="showHelp = false"
    />
  </div>
</template>
