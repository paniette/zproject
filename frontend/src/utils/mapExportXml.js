/**
 * Export minimal d’une carte en XML (interop / archivage).
 */

function esc (s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

export function mapPayloadToXml (payload) {
  const name = esc(payload.name || 'map')
  const pack = esc(payload.pack || '')
  const g = payload.grid || {}
  const lines = []
  lines.push('<?xml version="1.0" encoding="UTF-8"?>')
  lines.push(`<scenario name="${name}" pack="${pack}">`)
  lines.push(`  <grid width="${g.width ?? 0}" height="${g.height ?? 0}" tileSize="${g.tileSize ?? 0}" offsetX="${payload.gridOffsetX ?? 0}" offsetY="${payload.gridOffsetY ?? 0}"/>`)
  lines.push('  <tiles>')
  for (const t of payload.layers?.tiles || []) {
    lines.push(`    <tile id="${esc(t.id)}" x="${t.x}" y="${t.y}" rotation="${t.rotation ?? 0}" asset="${esc(t.asset)}"/>`)
  }
  lines.push('  </tiles>')
  lines.push('  <objects>')
  for (const o of payload.layers?.objects || []) {
    lines.push(`    <object id="${esc(o.id)}" type="${esc(o.type)}" x="${o.x}" y="${o.y}" rotation="${o.rotation ?? 0}" asset="${esc(o.asset)}"/>`)
  }
  lines.push('  </objects>')
  lines.push('</scenario>')
  return lines.join('\n')
}
