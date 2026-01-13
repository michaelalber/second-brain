import { describe, it, expect } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import RichEditor from '../RichEditor.vue'

describe('RichEditor', () => {
  it('renders with provided content', async () => {
    const wrapper = mount(RichEditor, {
      props: {
        modelValue: '<p>Hello World</p>',
      },
    })

    await flushPromises()
    await wrapper.vm.$nextTick()

    // Tiptap adds 'tiptap' class to the editor container
    expect(wrapper.find('.tiptap').exists()).toBe(true)
    expect(wrapper.text()).toContain('Hello World')
  })

  it('renders toolbar when not readonly', async () => {
    const wrapper = mount(RichEditor, {
      props: {
        modelValue: '<p>Test</p>',
        readonly: false,
      },
    })

    await flushPromises()
    await wrapper.vm.$nextTick()

    // EditorToolbar should be rendered
    expect(wrapper.findComponent({ name: 'EditorToolbar' }).exists()).toBe(true)
  })

  it('hides toolbar when readonly', async () => {
    const wrapper = mount(RichEditor, {
      props: {
        modelValue: '<p>Test</p>',
        readonly: true,
      },
    })

    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.findComponent({ name: 'EditorToolbar' }).exists()).toBe(false)
  })

  it('has rich-editor wrapper class', async () => {
    const wrapper = mount(RichEditor, {
      props: {
        modelValue: '<p>Hello</p>',
      },
    })

    expect(wrapper.find('.rich-editor').exists()).toBe(true)
  })

  it('editor content area exists after mount', async () => {
    const wrapper = mount(RichEditor, {
      props: {
        modelValue: '<p>Test content</p>',
      },
    })

    await flushPromises()
    await wrapper.vm.$nextTick()

    // ProseMirror is the actual contenteditable div
    expect(wrapper.find('.ProseMirror').exists()).toBe(true)
  })

  it('editor is not editable when readonly is true', async () => {
    const wrapper = mount(RichEditor, {
      props: {
        modelValue: '<p>Test</p>',
        readonly: true,
      },
    })

    await flushPromises()
    await wrapper.vm.$nextTick()

    const prosemirror = wrapper.find('.ProseMirror')
    expect(prosemirror.exists()).toBe(true)
    expect(prosemirror.attributes('contenteditable')).toBe('false')
  })

  it('editor is editable when readonly is false', async () => {
    const wrapper = mount(RichEditor, {
      props: {
        modelValue: '<p>Test</p>',
        readonly: false,
      },
    })

    await flushPromises()
    await wrapper.vm.$nextTick()

    const prosemirror = wrapper.find('.ProseMirror')
    expect(prosemirror.exists()).toBe(true)
    expect(prosemirror.attributes('contenteditable')).toBe('true')
  })
})
