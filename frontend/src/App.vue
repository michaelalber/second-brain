<script setup lang="ts">
import ParaSidebar from './components/ParaSidebar.vue'
</script>

<template>
  <div class="flex min-h-screen bg-gray-50">
    <ParaSidebar />
    <main class="flex-1 p-6 overflow-y-auto">
      <router-view />
    </main>
  </div>
</template>
