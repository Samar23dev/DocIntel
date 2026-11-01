export async function downloadSvgAsPng(svg: string, filename: string) {
  const parsed = new DOMParser().parseFromString(svg, 'image/svg+xml')
  const root = parsed.documentElement
  const viewBox = root.getAttribute('viewBox')?.trim().split(/[\s,]+/)
  const width = Number.parseFloat(root.getAttribute('width') || '') ||
    (viewBox?.length === 4 ? Number.parseFloat(viewBox[2]) : 1200)
  const height = Number.parseFloat(root.getAttribute('height') || '') ||
    (viewBox?.length === 4 ? Number.parseFloat(viewBox[3]) : 800)
  const safeWidth = Math.min(Math.max(width, 1), 8192)
  const safeHeight = Math.min(Math.max(height, 1), 8192)

  const svgBlob = new Blob([svg], { type: 'image/svg+xml;charset=utf-8' })
  const svgUrl = URL.createObjectURL(svgBlob)

  try {
    const image = await new Promise<HTMLImageElement>((resolve, reject) => {
      const element = new Image()
      element.onload = () => resolve(element)
      element.onerror = () => reject(new Error('Could not load the generated SVG image.'))
      element.src = svgUrl
    })

    const canvas = document.createElement('canvas')
    canvas.width = Math.ceil(safeWidth)
    canvas.height = Math.ceil(safeHeight)
    const context = canvas.getContext('2d')
    if (!context) throw new Error('PNG export is not supported by this browser.')
    context.drawImage(image, 0, 0, canvas.width, canvas.height)

    const pngBlob = await new Promise<Blob>((resolve, reject) => {
      canvas.toBlob((blob) => blob ? resolve(blob) : reject(new Error('Could not create the PNG image.')), 'image/png')
    })
    const pngUrl = URL.createObjectURL(pngBlob)
    const link = document.createElement('a')
    link.href = pngUrl
    link.download = filename
    link.click()
    URL.revokeObjectURL(pngUrl)
  } finally {
    URL.revokeObjectURL(svgUrl)
  }
}
