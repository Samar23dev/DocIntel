'use client'

import { useEffect, useRef, useState } from 'react'
import embed, { type Result, type VisualizationSpec } from 'vega-embed'
import { Check, ChevronDown, Copy, Download, RefreshCw } from 'lucide-react'
import { downloadSvgAsPng } from '@/lib/visualization-export'

function extractVegaSpec(source: string): VisualizationSpec {
  const trimmed = source.trim()
  try {
    return JSON.parse(trimmed) as VisualizationSpec
  } catch {
    const start = trimmed.indexOf('{')
    if (start < 0) throw new Error('No Vega-Lite JSON object was found.')

    let depth = 0
    let inString = false
    let escaped = false
    for (let index = start; index < trimmed.length; index += 1) {
      const character = trimmed[index]
      if (inString) {
        if (escaped) escaped = false
        else if (character === '\\') escaped = true
        else if (character === '"') inString = false
        continue
      }
      if (character === '"') inString = true
      else if (character === '{') depth += 1
      else if (character === '}') {
        depth -= 1
        if (depth === 0) {
          return JSON.parse(trimmed.slice(start, index + 1)) as VisualizationSpec
        }
      }
    }
    throw new Error('The Vega-Lite JSON object is incomplete.')
  }
}

export function VegaChart({
  code,
  onRegenerate,
}: {
  code: string
  onRegenerate?: (format?: 'mermaid' | 'dot' | 'vega-lite' | 'python-plot') => void
}) {
  const containerRef = useRef<HTMLDivElement>(null)
  const resultRef = useRef<Result | null>(null)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)
  const [formatMenuOpen, setFormatMenuOpen] = useState(false)

  useEffect(() => {
    let cancelled = false
    setError('')
    resultRef.current = null
    if (containerRef.current) containerRef.current.replaceChildren()

    try {
      const spec = extractVegaSpec(code)
      if (!containerRef.current) return

      embed(containerRef.current, spec, {
        actions: false,
        renderer: 'svg',
      }).then((result) => {
        if (!cancelled) resultRef.current = result
      }).catch((reason: unknown) => {
        if (!cancelled) {
          setError(reason instanceof Error ? reason.message : 'Invalid Vega-Lite specification.')
        }
      })
    } catch (reason) {
      if (!cancelled) {
        setError(reason instanceof Error ? reason.message : 'Invalid Vega-Lite JSON.')
      }
    }

    return () => { cancelled = true }
  }, [code])

  const downloadSvg = async () => {
    if (!resultRef.current) return
    const svg = await resultRef.current.view.toSVG()
    const url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml;charset=utf-8' }))
    const link = document.createElement('a')
    link.href = url
    link.download = 'docintel-chart.svg'
    link.click()
    URL.revokeObjectURL(url)
  }

  const downloadCode = () => {
    const url = URL.createObjectURL(new Blob([code.trim()], { type: 'application/json' }))
    const link = document.createElement('a')
    link.href = url
    link.download = 'docintel-chart.vega-lite.json'
    link.click()
    URL.revokeObjectURL(url)
  }

  if (error) {
    return (
      <div className="my-4 rounded-md border border-destructive/40 bg-muted p-3">
        <p className="mb-2 break-words text-sm text-destructive">Could not render this Vega-Lite chart: {error}</p>
        <div className="mb-3 flex gap-2">
          <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={downloadCode}><Download className="size-3.5" />Code</button>
          <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={() => { navigator.clipboard.writeText(code.trim()); setCopied(true); window.setTimeout(() => setCopied(false), 1500) }}>{copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}{copied ? 'Copied' : 'Copy'}</button>
        </div>
        <pre className="max-w-full overflow-x-auto whitespace-pre-wrap break-words text-sm"><code>{code}</code></pre>
      </div>
    )
  }

  return (
    <div className="my-4 rounded-md border border-border bg-card">
      <div className="flex justify-end gap-2 border-b border-border px-3 py-2">
        <span className="mr-auto rounded-full bg-muted px-2 py-1 text-[10px] font-medium uppercase tracking-wide text-muted-foreground">Vega-Lite</span>
        <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={async () => {
          const svg = await resultRef.current?.view.toSVG()
          if (svg) await downloadSvgAsPng(svg, 'docintel-chart.png')
        }}><Download className="size-3.5" />PNG</button>
        <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={downloadSvg}><Download className="size-3.5" />SVG</button>
        <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground" onClick={downloadCode}><Download className="size-3.5" />Code</button>
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
              </div>
            )}
          </div>
        )}
      </div>
      <div ref={containerRef} className="w-full max-w-full overflow-x-auto p-3 [&_svg]:mx-auto [&_svg]:block [&_svg]:h-auto [&_svg]:max-w-full" />
    </div>
  )
}
