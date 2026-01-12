import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'

export interface KeyboardShortcut {
  key: string
  description: string
  modifiers?: {
    ctrl?: boolean
    meta?: boolean
    shift?: boolean
    alt?: boolean
  }
}

export function useKeyboardShortcuts() {
  const router = useRouter()
  const showHelp = ref(false)

  const shortcuts: KeyboardShortcut[] = [
    { key: 'c', description: 'Quick capture (go to inbox)' },
    { key: '/', description: 'Focus search' },
    { key: 'g i', description: 'Go to inbox' },
    { key: 'g s', description: 'Go to search' },
    { key: 'g h', description: 'Go to home' },
    { key: 'e', description: 'Edit note (on note page)' },
    { key: 'm', description: 'Move note (on note page)' },
    { key: 'd', description: 'Delete note (on note page)' },
    { key: 'Ctrl+Enter', description: 'Save changes (while editing)' },
    { key: '?', description: 'Show keyboard shortcuts' },
    { key: 'Escape', description: 'Close dialogs / Cancel' },
  ]

  let pendingKey: string | null = null
  let pendingTimeout: number | null = null

  function isInputElement(element: EventTarget | null): boolean {
    if (!element) return false
    const tagName = (element as HTMLElement).tagName?.toLowerCase()
    return (
      tagName === 'input' ||
      tagName === 'textarea' ||
      tagName === 'select' ||
      (element as HTMLElement).isContentEditable
    )
  }

  function handleKeyDown(event: KeyboardEvent) {
    // Don't trigger shortcuts when typing in inputs
    if (isInputElement(event.target)) {
      // Only allow Escape in inputs
      if (event.key === 'Escape') {
        ;(event.target as HTMLElement).blur()
      }
      return
    }

    // Handle two-key sequences (g + letter)
    if (pendingKey === 'g') {
      clearTimeout(pendingTimeout!)
      pendingKey = null

      switch (event.key.toLowerCase()) {
        case 'i':
          event.preventDefault()
          router.push('/inbox')
          return
        case 's':
          event.preventDefault()
          router.push('/search')
          return
        case 'h':
          event.preventDefault()
          router.push('/')
          return
      }
    }

    // Start a two-key sequence
    if (event.key === 'g') {
      pendingKey = 'g'
      pendingTimeout = window.setTimeout(() => {
        pendingKey = null
      }, 1000)
      return
    }

    // Single-key shortcuts
    switch (event.key) {
      case 'c':
        event.preventDefault()
        router.push('/inbox')
        // Focus the title input after navigation
        setTimeout(() => {
          const titleInput = document.querySelector(
            'input[placeholder="Title"]'
          ) as HTMLInputElement
          titleInput?.focus()
        }, 100)
        break

      case '/':
        event.preventDefault()
        router.push('/search')
        // Focus the search input after navigation
        setTimeout(() => {
          const searchInput = document.querySelector(
            'input[type="text"][placeholder*="Search"]'
          ) as HTMLInputElement
          searchInput?.focus()
        }, 100)
        break

      case '?':
        event.preventDefault()
        showHelp.value = !showHelp.value
        break

      case 'Escape':
        showHelp.value = false
        break
    }
  }

  onMounted(() => {
    document.addEventListener('keydown', handleKeyDown)
  })

  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeyDown)
    if (pendingTimeout) {
      clearTimeout(pendingTimeout)
    }
  })

  return {
    shortcuts,
    showHelp,
  }
}
