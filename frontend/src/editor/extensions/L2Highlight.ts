import { Mark, mergeAttributes } from '@tiptap/core'

export interface L2HighlightOptions {
  HTMLAttributes: Record<string, unknown>
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    l2Highlight: {
      /**
       * Set L2 highlight mark (bold passage)
       */
      setL2Highlight: () => ReturnType
      /**
       * Toggle L2 highlight mark
       */
      toggleL2Highlight: () => ReturnType
      /**
       * Unset L2 highlight mark
       */
      unsetL2Highlight: () => ReturnType
    }
  }
}

export const L2Highlight = Mark.create<L2HighlightOptions>({
  name: 'l2Highlight',

  addOptions() {
    return {
      HTMLAttributes: {},
    }
  },

  parseHTML() {
    return [
      {
        tag: 'mark[data-l2-highlight]',
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    return [
      'mark',
      mergeAttributes(this.options.HTMLAttributes, HTMLAttributes, {
        'data-l2-highlight': '',
        class: 'l2-highlight',
      }),
      0,
    ]
  },

  addCommands() {
    return {
      setL2Highlight:
        () =>
        ({ commands }) => {
          return commands.setMark(this.name)
        },
      toggleL2Highlight:
        () =>
        ({ commands }) => {
          return commands.toggleMark(this.name)
        },
      unsetL2Highlight:
        () =>
        ({ commands }) => {
          return commands.unsetMark(this.name)
        },
    }
  },
})
