<script setup lang="ts">
import { onMounted } from 'vue'
import { useContainersStore } from '@/stores/containers'
import { storeToRefs } from 'pinia'

const containersStore = useContainersStore()
const { projects, areas, resources, archives, loading } = storeToRefs(containersStore)

onMounted(() => {
  containersStore.fetchContainers()
})
</script>

<template>
  <aside class="w-64 bg-gray-100 h-screen p-4 overflow-y-auto">
    <div class="mb-6">
      <router-link
        to="/"
        class="text-xl font-bold text-gray-800 hover:text-blue-600"
      >
        Second Brain
      </router-link>
    </div>

    <nav class="space-y-6">
      <!-- Quick Actions -->
      <div>
        <router-link
          to="/inbox"
          class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-200 text-gray-700"
        >
          <span>📥</span>
          <span>Inbox</span>
        </router-link>
        <router-link
          to="/search"
          class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-200 text-gray-700"
        >
          <span>🔍</span>
          <span>Search</span>
        </router-link>
      </div>

      <!-- PARA Sections -->
      <div v-if="loading" class="text-gray-500 text-sm">Loading...</div>

      <template v-else>
        <!-- Projects -->
        <div>
          <h3 class="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Projects
          </h3>
          <div v-if="projects.length === 0" class="px-3 text-sm text-gray-400">
            No projects
          </div>
          <router-link
            v-for="container in projects"
            :key="container.id"
            :to="`/containers/${container.id}`"
            class="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-200 text-gray-700"
          >
            <span class="truncate">{{ container.name }}</span>
            <span class="text-xs text-gray-400">{{ container.note_count }}</span>
          </router-link>
        </div>

        <!-- Areas -->
        <div>
          <h3 class="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Areas
          </h3>
          <div v-if="areas.length === 0" class="px-3 text-sm text-gray-400">
            No areas
          </div>
          <router-link
            v-for="container in areas"
            :key="container.id"
            :to="`/containers/${container.id}`"
            class="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-200 text-gray-700"
          >
            <span class="truncate">{{ container.name }}</span>
            <span class="text-xs text-gray-400">{{ container.note_count }}</span>
          </router-link>
        </div>

        <!-- Resources -->
        <div>
          <h3 class="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Resources
          </h3>
          <div v-if="resources.length === 0" class="px-3 text-sm text-gray-400">
            No resources
          </div>
          <router-link
            v-for="container in resources"
            :key="container.id"
            :to="`/containers/${container.id}`"
            class="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-200 text-gray-700"
          >
            <span class="truncate">{{ container.name }}</span>
            <span class="text-xs text-gray-400">{{ container.note_count }}</span>
          </router-link>
        </div>

        <!-- Archives -->
        <div v-if="archives.length > 0">
          <h3 class="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Archives
          </h3>
          <router-link
            v-for="container in archives"
            :key="container.id"
            :to="`/containers/${container.id}`"
            class="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-200 text-gray-500"
          >
            <span class="truncate">{{ container.name }}</span>
            <span class="text-xs text-gray-400">{{ container.note_count }}</span>
          </router-link>
        </div>
      </template>
    </nav>
  </aside>
</template>
