'use client'

import { useEffect, useId, useState } from 'react'
import mermaid from 'mermaid'

import { useThemeStore } from '@/lib/stores/theme-store'
import { Check, Copy, Download } from 'lucide-react'

export function MermaidDiagram({ code }: { code: string }) {
  const id = useId().replace(/:/g, '')
  const { getEffectiveTheme } = useThemeStore()
  const [svg, setSvg] = useState('')
  const [error, setError] = useState(false)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    let cancelled = false
    const diagram = code.trim()
    if (!diagram) return

    mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'strict',
      theme: getEffectiveTheme() === 'dark' ? 'dark' : 'default',
    })

    mermaid.render(`mermaid-${id}`, diagram).then(({ svg }) => {
      if (!cancelled) {
        setSvg(svg)
        setError(false)
      }
    }).catch(() => {
      if (!cancelled) setError(true)
    })

    return () => { cancelled = true }
  }, [code, getEffectiveTheme, id])

  if (error) {
    return (
      <div className="my-4 overflow-x-auto rounded-md border border-border bg-muted p-3">
        <p className="mb-2 text-sm text-destructive">Could not render this Mermaid diagram.</p>
        <pre className="text-sm"><code>{code}</code></pre>
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
        <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={() => download(svg, 'docintel-diagram.svg', 'image/svg+xml')}><Download className="size-3.5" />Image</button>
        <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={() => download(code.trim(), 'docintel-diagram.mmd', 'text/plain')}><Download className="size-3.5" />Code</button>
        <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={() => { navigator.clipboard.writeText(code.trim()); setCopied(true); window.setTimeout(() => setCopied(false), 1500) }}>{copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}{copied ? 'Copied' : 'Copy'}</button>
      </div>
      <div className="overflow-x-auto p-3 [&>svg]:mx-auto [&>svg]:max-w-full" dangerouslySetInnerHTML={{ __html: svg }} />
    </div>
  )
}
