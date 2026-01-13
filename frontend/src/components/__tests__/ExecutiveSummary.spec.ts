import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ExecutiveSummary from '../ExecutiveSummary.vue'

describe('ExecutiveSummary', () => {
  it('renders with provided summary text', () => {
    const wrapper = mount(ExecutiveSummary, {
      props: {
        modelValue: 'This is my executive summary',
      },
    })

    expect(wrapper.text()).toContain('Executive Summary')
  })

  it('shows textarea when not readonly', () => {
    const wrapper = mount(ExecutiveSummary, {
      props: {
        modelValue: 'Summary text',
        readonly: false,
      },
    })

    expect(wrapper.find('textarea').exists()).toBe(true)
  })

  it('shows text display when readonly', () => {
    const wrapper = mount(ExecutiveSummary, {
      props: {
        modelValue: 'Summary text',
        readonly: true,
      },
    })

    expect(wrapper.find('textarea').exists()).toBe(false)
    expect(wrapper.text()).toContain('Summary text')
  })

  it('emits update:modelValue when textarea changes', async () => {
    const wrapper = mount(ExecutiveSummary, {
      props: {
        modelValue: '',
        readonly: false,
      },
    })

    const textarea = wrapper.find('textarea')
    await textarea.setValue('New summary content')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['New summary content'])
  })

  it('has L4 label indicator', () => {
    const wrapper = mount(ExecutiveSummary, {
      props: {
        modelValue: '',
      },
    })

    expect(wrapper.text()).toContain('L4')
  })

  it('shows placeholder when empty and not readonly', () => {
    const wrapper = mount(ExecutiveSummary, {
      props: {
        modelValue: '',
        readonly: false,
      },
    })

    const textarea = wrapper.find('textarea')
    expect(textarea.attributes('placeholder')).toBeTruthy()
  })

  it('shows empty state message when readonly and no summary', () => {
    const wrapper = mount(ExecutiveSummary, {
      props: {
        modelValue: '',
        readonly: true,
      },
    })

    expect(wrapper.text()).toContain('No executive summary')
  })
})
