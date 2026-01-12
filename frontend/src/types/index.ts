// PARA Container Types
export type ContainerType = 'project' | 'area' | 'resource' | 'archive'

// CODE Workflow Stages
export type CodeStage = 'capture' | 'organize' | 'distill' | 'express'

// Highlight Range for Progressive Summarization
export interface HighlightRange {
  start: number
  end: number
  layer: 2 | 3
}

// Note Types
export interface Note {
  id: string
  title: string
  content: string
  content_html?: string | null
  highlights: { highlights?: HighlightRange[] }
  executive_summary?: string | null
  source_url?: string | null
  source_type?: string | null
  container_id?: string | null
  code_stage: CodeStage
  created_at: string
  updated_at: string
  captured_at: string
}

export interface NoteCreate {
  title: string
  content: string
  source_url?: string
  source_type?: string
}

export interface NoteUpdate {
  title?: string
  content?: string
  content_html?: string
  source_url?: string
  source_type?: string
  executive_summary?: string
}

export interface NoteMoveRequest {
  container_id: string | null
}

export interface NoteHighlightsUpdate {
  highlights: HighlightRange[]
}

// Container Types
export interface Container {
  id: string
  name: string
  type: ContainerType
  description?: string | null
  parent_id?: string | null
  is_active: boolean
  deadline?: string | null
  status?: string | null
  created_at: string
  updated_at: string
}

export interface ContainerCreate {
  name: string
  type: ContainerType
  description?: string
  parent_id?: string
  deadline?: string
  status?: string
}

export interface ContainerUpdate {
  name?: string
  type?: ContainerType
  description?: string
  parent_id?: string
  is_active?: boolean
  deadline?: string
  status?: string
}

export interface ContainerWithCount extends Container {
  note_count: number
}

export interface ContainerWithNotes extends Container {
  notes: Note[]
}
