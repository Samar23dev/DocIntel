'use client'

import { useEffect, useState } from 'react'
import { Check, Copy, Download } from 'lucide-react'

function sanitizeSvg(svg: string) {
  const document = new DOMParser().parseFromString(svg, 'image/svg+xml')
  document.querySelectorAll('script, foreignObject, iframe, object, embed').forEach((element) => element.remove())
  return new XMLSerializer().serializeToString(document.documentElement)
}

export function PythonPlot({ code }: { code: string }) {
  const [svg, setSvg] = useState('')
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    let cancelled = false
    setSvg('')
    setError('')

    fetch('/api/python/plot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code }),
    }).then(async (response) => {
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Plot generation failed')
      if (!cancelled) setSvg(sanitizeSvg(data.svg))
    }).catch((reason) => {
      if (!cancelled) setError(reason instanceof Error ? reason.message : 'Plot generation failed')
    })

    return () => { cancelled = true }
  }, [code])

  if (error) {
    return (
      <div className="my-4 overflow-x-auto rounded-md border border-destructive/40 bg-muted p-3">
        <p className="mb-2 text-sm text-destructive">Could not generate this plot: {error}</p>
        <pre className="text-sm"><code>{code}</code></pre>
      </div>
    )
  }

  if (!svg) return <div className="my-4 text-sm text-muted-foreground">Generating plot…</div>

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
        <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={() => download(svg, 'docintel-chart.svg', 'image/svg+xml')}><Download className="size-3.5" />Image</button>
        <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={() => download(code.trim(), 'docintel-chart.py', 'text/x-python')}><Download className="size-3.5" />Code</button>
        <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={() => { navigator.clipboard.writeText(code.trim()); setCopied(true); window.setTimeout(() => setCopied(false), 1500) }}>{copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}{copied ? 'Copied' : 'Copy'}</button>
      </div>
      <div className="overflow-x-auto p-3 [&>svg]:mx-auto [&>svg]:max-w-full" dangerouslySetInnerHTML={{ __html: svg }} />
    </div>
  )
}
