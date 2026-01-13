import { describe, it, expect } from 'vitest'
import { Editor } from '@tiptap/core'
import StarterKit from '@tiptap/starter-kit'
import { L2Highlight } from '../L2Highlight'
import { L3Highlight } from '../L3Highlight'

function createEditor(content: string = '<p>Hello World</p>') {
  return new Editor({
    extensions: [StarterKit, L2Highlight, L3Highlight],
    content,
  })
}

describe('L2Highlight Extension', () => {
  it('can be toggled on selected text', () => {
    const editor = createEditor('<p>Hello World</p>')

    // Select "Hello"
    editor.commands.setTextSelection({ from: 1, to: 6 })
    editor.commands.toggleL2Highlight()

    expect(editor.isActive('l2Highlight')).toBe(true)
    expect(editor.getHTML()).toContain('data-l2-highlight')
  })

  it('can be toggled off', () => {
    const editor = createEditor('<p>Hello World</p>')

    // Select and toggle on
    editor.commands.setTextSelection({ from: 1, to: 6 })
    editor.commands.toggleL2Highlight()

    // Toggle off
    editor.commands.toggleL2Highlight()

    expect(editor.isActive('l2Highlight')).toBe(false)
  })

  it('renders with correct HTML tag and attributes', () => {
    const editor = createEditor('<p>Hello World</p>')

    editor.commands.setTextSelection({ from: 1, to: 6 })
    editor.commands.toggleL2Highlight()

    const html = editor.getHTML()
    expect(html).toContain('<mark')
    expect(html).toContain('data-l2-highlight')
  })
})

describe('L3Highlight Extension', () => {
  it('can be toggled on selected text', () => {
    const editor = createEditor('<p>Hello World</p>')

    // Select "Hello"
    editor.commands.setTextSelection({ from: 1, to: 6 })
    editor.commands.toggleL3Highlight()

    expect(editor.isActive('l3Highlight')).toBe(true)
    expect(editor.getHTML()).toContain('data-l3-highlight')
  })

  it('can be toggled off', () => {
    const editor = createEditor('<p>Hello World</p>')

    // Select and toggle on
    editor.commands.setTextSelection({ from: 1, to: 6 })
    editor.commands.toggleL3Highlight()

    // Toggle off
    editor.commands.toggleL3Highlight()

    expect(editor.isActive('l3Highlight')).toBe(false)
  })

  it('renders with correct HTML tag and attributes', () => {
    const editor = createEditor('<p>Hello World</p>')

    editor.commands.setTextSelection({ from: 1, to: 6 })
    editor.commands.toggleL3Highlight()

    const html = editor.getHTML()
    expect(html).toContain('<mark')
    expect(html).toContain('data-l3-highlight')
  })
})

describe('L2 and L3 together', () => {
  it('can have both L2 and L3 applied to same text', () => {
    const editor = createEditor('<p>Hello World</p>')

    // Select "Hello"
    editor.commands.setTextSelection({ from: 1, to: 6 })
    editor.commands.toggleL2Highlight()
    editor.commands.toggleL3Highlight()

    expect(editor.isActive('l2Highlight')).toBe(true)
    expect(editor.isActive('l3Highlight')).toBe(true)
  })

  it('can apply L3 within L2 highlighted text', () => {
    const editor = createEditor('<p>Hello World</p>')

    // Apply L2 to "Hello World"
    editor.commands.setTextSelection({ from: 1, to: 12 })
    editor.commands.toggleL2Highlight()

    // Apply L3 to just "Hello"
    editor.commands.setTextSelection({ from: 1, to: 6 })
    editor.commands.toggleL3Highlight()

    const html = editor.getHTML()
    expect(html).toContain('data-l2-highlight')
    expect(html).toContain('data-l3-highlight')
  })
})
