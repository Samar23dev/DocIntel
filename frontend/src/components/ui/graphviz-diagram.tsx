'use client'

import { useEffect, useState } from 'react'
import { instance } from '@viz-js/viz'
import { Check, ChevronDown, Copy, Download, RefreshCw } from 'lucide-react'
import { downloadSvgAsPng } from '@/lib/visualization-export'

export function GraphvizDiagram({
  code,
  onRegenerate,
}: {
  code: string
  onRegenerate?: (format?: 'mermaid' | 'dot' | 'vega-lite' | 'python-plot' | 'plotly-plot') => void
}) {
  const [svg, setSvg] = useState('')
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)
  const [formatMenuOpen, setFormatMenuOpen] = useState(false)

  useEffect(() => {
    let cancelled = false
    setSvg('')
    setError('')

    instance().then((viz) => {
      const rendered = viz.renderSVGElement(code)
      if (!cancelled) setSvg(rendered.outerHTML)
    }).catch((reason: unknown) => {
      console.error('Graphviz render failed', reason)
      if (!cancelled) setError('The generated diagram is invalid. Please try regenerating it.')
    })

    return () => { cancelled = true }
  }, [code])

  if (error) {
    return (
      <div className="my-4 rounded-md border border-destructive/40 bg-muted p-3">
        <p className="mb-2 break-words text-sm text-destructive">Could not render this Graphviz diagram: {error}</p>
        <pre className="max-w-full overflow-x-auto whitespace-pre-wrap break-words text-sm"><code>{code}</code></pre>
      </div>
    )
  }

  if (!svg) return <div className="my-4 text-sm text-muted-foreground">Rendering Graphviz diagram…</div>

  const download = (content: string, filename: string, type: string) => {
    const url = URL.createObjectURL(new Blob([content], { type }))
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="my-4 overflow-hidden rounded-md border border-border bg-card">
      <div className="flex justify-end gap-2 border-b border-border px-3 py-2">
        <span className="mr-auto rounded-full bg-muted px-2 py-1 text-[10px] font-medium uppercase tracking-wide text-muted-foreground">Graphviz DOT</span>
        <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={() => downloadSvgAsPng(svg, 'docintel-diagram.png')}><Download className="size-3.5" />PNG</button>
        <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={() => download(svg, 'docintel-diagram.svg', 'image/svg+xml')}><Download className="size-3.5" />SVG</button>
        <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground" onClick={() => download(code.trim(), 'docintel-diagram.dot', 'text/vnd.graphviz')}><Download className="size-3.5" />Code</button>
        <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground" onClick={() => { navigator.clipboard.writeText(code.trim()); setCopied(true); window.setTimeout(() => setCopied(false), 1500) }}>{copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}{copied ? 'Copied' : 'Copy'}</button>
        {onRegenerate && (
          <div className="relative">
            <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={() => setFormatMenuOpen((open) => !open)} aria-expanded={formatMenuOpen}>
              <RefreshCw className="size-3.5" />Regenerate <ChevronDown className="size-3" />
            </button>
            {formatMenuOpen && (
              <div className="absolute right-0 top-full z-50 mt-1 w-44 rounded-md border border-border bg-popover p-1 text-popover-foreground shadow-xl">
                <button type="button" className="block w-full rounded px-2 py-1.5 text-left text-xs hover:bg-accent" onClick={() => { setFormatMenuOpen(false); onRegenerate?.('dot') }}>Graphviz DOT</button>
                <button type="button" className="block w-full rounded px-2 py-1.5 text-left text-xs hover:bg-accent" onClick={() => { setFormatMenuOpen(false); onRegenerate?.('vega-lite') }}>Vega-Lite</button>
                <button type="button" className="block w-full rounded px-2 py-1.5 text-left text-xs hover:bg-accent" onClick={() => { setFormatMenuOpen(false); onRegenerate?.('python-plot') }}>Matplotlib / Python</button>
                <button type="button" className="block w-full rounded px-2 py-1.5 text-left text-xs hover:bg-accent" onClick={() => { setFormatMenuOpen(false); onRegenerate?.('plotly-plot') }}>Plotly / Python</button>
              </div>
            )}
          </div>
        )}
      </div>
      <div className="overflow-x-auto p-3 [&>svg]:mx-auto [&>svg]:block [&>svg]:h-auto [&>svg]:max-w-full" dangerouslySetInnerHTML={{ __html: svg }} />
    </div>
  )
}
