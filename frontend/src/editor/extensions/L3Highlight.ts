import { Mark, mergeAttributes } from '@tiptap/core'

export interface L3HighlightOptions {
  HTMLAttributes: Record<string, unknown>
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    l3Highlight: {
      /**
       * Set L3 highlight mark (key insight)
       */
      setL3Highlight: () => ReturnType
      /**
       * Toggle L3 highlight mark
       */
      toggleL3Highlight: () => ReturnType
      /**
       * Unset L3 highlight mark
       */
      unsetL3Highlight: () => ReturnType
    }
  }
}

export const L3Highlight = Mark.create<L3HighlightOptions>({
  name: 'l3Highlight',

  addOptions() {
    return {
      HTMLAttributes: {},
    }
  },

  parseHTML() {
    return [
      {
        tag: 'mark[data-l3-highlight]',
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    return [
      'mark',
      mergeAttributes(this.options.HTMLAttributes, HTMLAttributes, {
        'data-l3-highlight': '',
        class: 'l3-highlight',
      }),
      0,
    ]
  },

  addCommands() {
    return {
      setL3Highlight:
        () =>
        ({ commands }) => {
          return commands.setMark(this.name)
        },
      toggleL3Highlight:
        () =>
        ({ commands }) => {
          return commands.toggleMark(this.name)
        },
      unsetL3Highlight:
        () =>
        ({ commands }) => {
          return commands.unsetMark(this.name)
        },
    }
  },
})
