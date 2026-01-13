import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { Editor } from '@tiptap/core'
import StarterKit from '@tiptap/starter-kit'
import EditorToolbar from '../EditorToolbar.vue'
import { L2Highlight } from '@/editor/extensions/L2Highlight'
import { L3Highlight } from '@/editor/extensions/L3Highlight'

function createEditor(content: string = '<p>Hello World</p>') {
  return new Editor({
    extensions: [StarterKit, L2Highlight, L3Highlight],
    content,
  })
}

describe('EditorToolbar', () => {
  let editor: Editor

  beforeEach(() => {
    editor = createEditor()
  })

  afterEach(() => {
    editor.destroy()
  })

  it('renders formatting buttons', () => {
    const wrapper = mount(EditorToolbar, {
      props: { editor },
    })

    expect(wrapper.find('[data-testid="btn-bold"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="btn-italic"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="btn-h1"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="btn-h2"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="btn-h3"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="btn-bullet-list"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="btn-ordered-list"]').exists()).toBe(true)
  })

  it('renders highlight buttons', () => {
    const wrapper = mount(EditorToolbar, {
      props: { editor },
    })

    expect(wrapper.find('[data-testid="btn-l2"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="btn-l3"]').exists()).toBe(true)
  })

  it('has correct button titles for accessibility', () => {
    const wrapper = mount(EditorToolbar, {
      props: { editor },
    })

    expect(wrapper.find('[data-testid="btn-bold"]').attributes('title')).toContain('Bold')
    expect(wrapper.find('[data-testid="btn-italic"]').attributes('title')).toContain('Italic')
    expect(wrapper.find('[data-testid="btn-l2"]').attributes('title')).toContain('L2')
    expect(wrapper.find('[data-testid="btn-l3"]').attributes('title')).toContain('L3')
  })

  it('L2 button has distinctive styling', () => {
    const wrapper = mount(EditorToolbar, {
      props: { editor },
    })

    const l2Btn = wrapper.find('[data-testid="btn-l2"]')
    expect(l2Btn.classes()).toContain('l2-btn')
  })

  it('L3 button has distinctive styling', () => {
    const wrapper = mount(EditorToolbar, {
      props: { editor },
    })

    const l3Btn = wrapper.find('[data-testid="btn-l3"]')
    expect(l3Btn.classes()).toContain('l3-btn')
  })

  it('all buttons are of type button (not submit)', () => {
    const wrapper = mount(EditorToolbar, {
      props: { editor },
    })

    const buttons = wrapper.findAll('button')
    buttons.forEach((btn) => {
      expect(btn.attributes('type')).toBe('button')
    })
  })
})
