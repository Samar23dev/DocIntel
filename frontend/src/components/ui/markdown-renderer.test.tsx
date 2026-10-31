import { describe, it, expect, vi } from 'vitest'
import { render, waitFor } from '@testing-library/react'

import { MarkdownRenderer } from './markdown-renderer'

describe('MarkdownRenderer', () => {
  it('renders basic markdown', () => {
    const { container } = render(<MarkdownRenderer>{'# Title\n\nSome **bold** text'}</MarkdownRenderer>)
    expect(container.querySelector('h1')?.textContent).toBe('Title')
    expect(container.querySelector('strong')?.textContent).toBe('bold')
  })

  it('highlights fenced code blocks for registered languages', () => {
    const { container } = render(
      <MarkdownRenderer>{'```python\ndef hello():\n    return 42\n```'}</MarkdownRenderer>
    )
    // PrismLight emits token spans when the grammar is registered; a plain
    // fallback would leave the code block without any token markup.
    expect(container.querySelectorAll('span[class*="token"]').length).toBeGreaterThan(0)
  })

  it('falls back to plain text for unknown languages without crashing', () => {
    const { container } = render(
      <MarkdownRenderer>{'```notalanguage\nsome content\n```'}</MarkdownRenderer>
    )
    expect(container.textContent).toContain('some content')
  })

  it('renders inline code without a highlighter block', () => {
    const { container } = render(<MarkdownRenderer>{'Use `npm ci` here'}</MarkdownRenderer>)
    expect(container.querySelector('code')?.textContent).toBe('npm ci')
    expect(container.querySelectorAll('span[class*="token"]').length).toBe(0)
  })

  it('sends python-plot blocks to the plot renderer', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({
      svg: '<svg xmlns="http://www.w3.org/2000/svg"><circle cx="5" cy="5" r="4" /></svg>'
    }), { status: 200, headers: { 'Content-Type': 'application/json' } })))

    const { container } = render(
      <MarkdownRenderer>{'```python-plot\nimport matplotlib.pyplot as plt\nplt.plot([1, 2])\n```'}</MarkdownRenderer>
    )

    await waitFor(() => expect(container.querySelector('svg')).not.toBeNull())
    vi.unstubAllGlobals()
  })
})
