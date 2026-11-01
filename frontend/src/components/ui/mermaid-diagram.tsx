'use client'

import { useEffect, useId, useState } from 'react'
import mermaid from 'mermaid'

import { useThemeStore } from '@/lib/stores/theme-store'
import { Check, ChevronDown, Copy, Download, RefreshCw } from 'lucide-react'
import { downloadSvgAsPng } from '@/lib/visualization-export'

let renderQueue = Promise.resolve()

function sanitizeSvg(svg: string) {
  const document = new DOMParser().parseFromString(svg, 'image/svg+xml')
  document.querySelectorAll('script, iframe, object, embed').forEach((element) => element.remove())
  document.querySelectorAll('foreignObject a, foreignObject form, foreignObject input, foreignObject button, foreignObject textarea').forEach((element) => element.remove())
  return new XMLSerializer().serializeToString(document.documentElement)
}

export function MermaidDiagram({
  code,
  onRegenerate,
}: {
  code: string
  onRegenerate?: (format?: 'mermaid' | 'dot' | 'vega-lite' | 'python-plot') => void
}) {
  const id = useId().replace(/:/g, '')
  const { getEffectiveTheme } = useThemeStore()
  const [svg, setSvg] = useState('')
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)
  const [formatMenuOpen, setFormatMenuOpen] = useState(false)

  useEffect(() => {
    let cancelled = false
    const diagram = code.trim()
    if (!diagram) return

    const renderJob = renderQueue.then(async () => {
      mermaid.initialize({
        startOnLoad: false,
        securityLevel: 'strict',
        theme: getEffectiveTheme() === 'dark' ? 'dark' : 'default',
        suppressErrorRendering: true,
      })
      await mermaid.parse(diagram, { suppressErrors: true })
      return mermaid.render(`mermaid-${id}`, diagram)
    })
    renderQueue = renderJob.then(() => undefined, () => undefined)

    renderJob.then(({ svg }) => {
      if (!cancelled) {
        setSvg(sanitizeSvg(svg))
        setError('')
      }
    }).catch((reason: unknown) => {
      if (!cancelled) {
        const message = reason instanceof Error ? reason.message : 'Invalid Mermaid syntax.'
        setError(message.replace(/^.*\n/, '').trim() || 'Invalid Mermaid syntax.')
      }
    })

    return () => { cancelled = true }
  }, [code, getEffectiveTheme, id])

  if (error) {
    return (
      <div className="my-4 overflow-x-auto rounded-md border border-border bg-muted p-3">
        <p className="mb-2 break-words text-sm text-destructive">Could not render this Mermaid diagram: {error}</p>
        {onRegenerate && (
          <button type="button" className="mb-2 inline-flex items-center gap-1 rounded-md border border-border bg-background px-3 py-1.5 text-sm hover:bg-muted" onClick={() => onRegenerate?.('mermaid')}>
            <RefreshCw className="size-3.5" /> Regenerate
          </button>
        )}
        <pre className="max-w-full overflow-x-auto whitespace-pre-wrap break-words text-sm"><code>{code}</code></pre>
      </div>
    )
  }

  if (!svg) return <div className="my-4 text-sm text-muted-foreground">Rendering diagram…</div>

  const download = (content: string, filename: string, type: string) => {
    const url = URL.createObjectURL(new Blob([content], { type }))
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="my-4 rounded-md border border-border bg-card">
      <div className="flex justify-end gap-2 border-b border-border px-3 py-2">
        <span className="mr-auto rounded-full bg-muted px-2 py-1 text-[10px] font-medium uppercase tracking-wide text-muted-foreground">Mermaid</span>
        <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={() => downloadSvgAsPng(svg, 'docintel-diagram.png')}><Download className="size-3.5" />PNG</button>
        <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={() => download(svg, 'docintel-diagram.svg', 'image/svg+xml')}><Download className="size-3.5" />SVG</button>
        <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={() => download(code.trim(), 'docintel-diagram.mmd', 'text/plain')}><Download className="size-3.5" />Code</button>
        <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={() => { navigator.clipboard.writeText(code.trim()); setCopied(true); window.setTimeout(() => setCopied(false), 1500) }}>{copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}{copied ? 'Copied' : 'Copy'}</button>
        {onRegenerate && (
          <div className="relative">
            <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={() => setFormatMenuOpen((open) => !open)} aria-expanded={formatMenuOpen}>
              <RefreshCw className="size-3.5" />Regenerate <ChevronDown className="size-3" />
            </button>
            {formatMenuOpen && (
              <div className="absolute right-0 top-full z-50 mt-1 w-44 rounded-md border border-border bg-popover p-1 text-popover-foreground shadow-xl">
                <button type="button" className="block w-full rounded px-2 py-1.5 text-left text-xs hover:bg-muted" onClick={() => { setFormatMenuOpen(false); onRegenerate?.('mermaid') }}>Mermaid</button>
                <button type="button" className="block w-full rounded px-2 py-1.5 text-left text-xs hover:bg-muted" onClick={() => { setFormatMenuOpen(false); onRegenerate?.('dot') }}>Graphviz DOT</button>
                <button type="button" className="block w-full rounded px-2 py-1.5 text-left text-xs hover:bg-muted" onClick={() => { setFormatMenuOpen(false); onRegenerate?.('vega-lite') }}>Vega-Lite</button>
              </div>
            )}
          </div>
        )}
      </div>
      <div className="w-full max-w-full overflow-x-auto p-3 [&>svg]:mx-auto [&>svg]:block [&>svg]:h-auto [&>svg]:max-w-full [&>svg]:[max-height:70vh]" dangerouslySetInnerHTML={{ __html: svg }} />
    </div>
  )
}
