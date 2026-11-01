'use client'

import { useEffect, useRef, useState } from 'react'
import { Check, Copy, Download, RefreshCw } from 'lucide-react'
import Plotly from 'plotly.js-dist-min'

type VisualizationFormat = 'mermaid' | 'dot' | 'vega-lite' | 'python-plot' | 'plotly-plot'

interface PlotlyFigure {
  data: Plotly.Data[]
  layout?: Partial<Plotly.Layout>
  config?: Partial<Plotly.Config>
}

export function PlotlyPlot({ code, onRegenerate }: { code: string; onRegenerate?: (format?: VisualizationFormat) => void }) {
  const chartRef = useRef<HTMLDivElement>(null)
  const [figure, setFigure] = useState<PlotlyFigure | null>(null)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    let cancelled = false
    setFigure(null)
    setError('')

    fetch('/api/python/plotly', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code }),
    }).then(async (response) => {
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Plotly generation failed')
      if (!cancelled) setFigure(data.figure as PlotlyFigure)
    }).catch((reason) => {
      console.error('Plotly render failed', reason)
      if (!cancelled) setError('The generated chart could not be rendered. Please try regenerating it.')
    })
  }, [code])

  useEffect(() => {
    if (!figure || !chartRef.current) return
    Plotly.react(chartRef.current, figure.data, figure.layout, { responsive: true, ...figure.config })
    return () => { if (chartRef.current) Plotly.purge(chartRef.current) }
  }, [figure])

  const downloadCode = () => {
    const url = URL.createObjectURL(new Blob([code.trim()], { type: 'text/x-python' }))
    const link = document.createElement('a')
    link.href = url
    link.download = 'docintel-chart.plotly.py'
    link.click()
    URL.revokeObjectURL(url)
  }

  if (error) {
    return <div className="my-4 rounded-md border border-destructive/40 bg-muted p-3 text-sm text-destructive">Could not generate this Plotly chart: {error}</div>
  }

  return (
    <div className="my-4 rounded-md border border-border bg-card">
      <div className="flex justify-end gap-2 border-b border-border px-3 py-2">
        <span className="mr-auto rounded-full bg-muted px-2 py-1 text-[10px] font-medium uppercase tracking-wide text-muted-foreground">Plotly</span>
        <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={() => chartRef.current && Plotly.downloadImage(chartRef.current, { format: 'png', filename: 'docintel-chart' })}><Download className="size-3.5" />PNG</button>
        <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={downloadCode}><Download className="size-3.5" />Code</button>
        <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={() => { navigator.clipboard.writeText(code.trim()); setCopied(true); window.setTimeout(() => setCopied(false), 1500) }}>{copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}{copied ? 'Copied' : 'Copy'}</button>
        {onRegenerate && <button type="button" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={() => onRegenerate('plotly-plot')}><RefreshCw className="size-3.5" />Regenerate</button>}
      </div>
      {!figure && <div className="p-3 text-sm text-muted-foreground">Generating Plotly chart…</div>}
      <div ref={chartRef} className="min-h-[320px] w-full p-2" />
    </div>
  )
}
