import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useContainersStore } from '../containers'
import * as client from '@/api/client'

// Mock the API client
vi.mock('@/api/client', () => ({
  containersApi: {
    create: vi.fn(),
    list: vi.fn(),
    get: vi.fn(),
    update: vi.fn(),
    archive: vi.fn(),
    delete: vi.fn(),
  },
}))

const mockContainer = {
  id: 'container-1',
  name: 'Test Project',
  type: 'project' as const,
  is_active: true,
  note_count: 5,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

describe('Containers Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetches containers and populates PARA', async () => {
    const store = useContainersStore()

    const containers = [
      { ...mockContainer, id: '1', type: 'project' as const },
      { ...mockContainer, id: '2', type: 'area' as const },
      { ...mockContainer, id: '3', type: 'resource' as const },
      { ...mockContainer, id: '4', type: 'archive' as const },
    ]

    vi.mocked(client.containersApi.list).mockResolvedValue(containers)

    await store.fetchContainers()

    expect(client.containersApi.list).toHaveBeenCalled()
    expect(store.containers).toHaveLength(4)
    expect(store.projects).toHaveLength(1)
    expect(store.areas).toHaveLength(1)
    expect(store.resources).toHaveLength(1)
    expect(store.archives).toHaveLength(1)
  })

  it('creates container and refetches list', async () => {
    const store = useContainersStore()

    vi.mocked(client.containersApi.create).mockResolvedValue(mockContainer)
    vi.mocked(client.containersApi.list).mockResolvedValue([
      { ...mockContainer, note_count: 0 },
    ])

    await store.createContainer({ name: 'New Project', type: 'project' })

    expect(client.containersApi.create).toHaveBeenCalledWith({
      name: 'New Project',
      type: 'project',
    })
    expect(client.containersApi.list).toHaveBeenCalled()
  })

  it('archives container and updates type', async () => {
    const store = useContainersStore()
    const archivedContainer = {
      ...mockContainer,
      type: 'archive' as const,
      is_active: false,
    }

    store.containers = [mockContainer]

    vi.mocked(client.containersApi.archive).mockResolvedValue(archivedContainer)

    await store.archiveContainer('container-1')

    expect(client.containersApi.archive).toHaveBeenCalledWith('container-1')
    expect(store.containers[0].type).toBe('archive')
    expect(store.containers[0].is_active).toBe(false)
  })

  it('deletes container and removes from list', async () => {
    const store = useContainersStore()
    store.containers = [mockContainer]

    vi.mocked(client.containersApi.delete).mockResolvedValue(undefined)

    await store.deleteContainer('container-1')

    expect(client.containersApi.delete).toHaveBeenCalledWith('container-1')
    expect(store.containers).toHaveLength(0)
  })

  it('calculates total note count', () => {
    const store = useContainersStore()
    store.containers = [
      { ...mockContainer, id: '1', note_count: 5 },
      { ...mockContainer, id: '2', note_count: 3 },
      { ...mockContainer, id: '3', note_count: 7 },
    ]

    expect(store.totalNoteCount).toBe(15)
  })

  it('byType getter filters correctly', () => {
    const store = useContainersStore()
    store.containers = [
      { ...mockContainer, id: '1', type: 'project' as const },
      { ...mockContainer, id: '2', type: 'area' as const },
      { ...mockContainer, id: '3', type: 'project' as const },
    ]

    expect(store.byType('project')).toHaveLength(2)
    expect(store.byType('area')).toHaveLength(1)
    expect(store.byType('resource')).toHaveLength(0)
  })
})
