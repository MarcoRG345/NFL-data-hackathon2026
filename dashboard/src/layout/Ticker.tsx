// Cinta superior con jugadas clave

import { useEffect, useState } from 'react'
import { getResumen, getCarreraResultado, getGirosResumen, getVueloResumen } from '../api'

export default function Ticker() {
  const [frases, setFrases] = useState<string[]>([])

  useEffect(() => {
    const cargarFrases = async () => {
      const resultado: string[] = []

      // Resumen
      try {
        const data = await getResumen('decisivo', 'ofe')
        if (data.kpis.pct_gana_receptor !== null) {
          resultado.push(`Gana receptor ${data.kpis.pct_gana_receptor.toFixed(1)}% · n=${data.n}`)
        }
        if (data.kpis.conv_gana_receptor !== null && data.kpis.conv_gana_defensa !== null) {
          const dif = data.kpis.conv_gana_receptor - data.kpis.conv_gana_defensa
          resultado.push(`Conversión gana receptor vs defensa: +${dif.toFixed(1)} pts`)
        }
      } catch {}

      // Carrera resultado
      try {
        const data = await getCarreraResultado('decisivo')
        if (data.pct_gana_receptor !== null) {
          resultado.push(`Receptor libre primero: ${data.pct_gana_receptor.toFixed(1)}%`)
        }
        if (data.pct_sin_presion !== null) {
          resultado.push(`Sin presión: ${data.pct_sin_presion.toFixed(1)}%`)
        }
      } catch {}

      // Giros
      try {
        const data = await getGirosResumen('decisivo')
        const brusco = data.por_tipo.find(t => t.tipo === 'brusco')
        const sinGiro = data.por_tipo.find(t => t.tipo === 'sin_giro')
        if (brusco && sinGiro && brusco.sep_ganada !== null && sinGiro.sep_ganada !== null) {
          const dif = brusco.sep_ganada - sinGiro.sep_ganada
          resultado.push(`Giro brusco vs sin giro: ${dif > 0 ? '+' : ''}${dif.toFixed(2)} yd`)
        }
      } catch {}

      // Vuelo
      try {
        const data = await getVueloResumen('decisivo')
        const abierto = data.por_separacion.find(s => s.franja === 'abierto')
        const cerrado = data.por_separacion.find(s => s.franja === 'cerrado')
        if (abierto && cerrado && abierto.pct_completo !== null && cerrado.pct_completo !== null) {
          const dif = abierto.pct_completo - cerrado.pct_completo
          resultado.push(`Abierto al lanzar: +${dif.toFixed(1)} pts de completo`)
        }
      } catch {}

      setFrases(resultado.length > 0 ? resultado : ['Cargando datos...'])
    }

    cargarFrases()
  }, [])

  if (frases.length === 0) return null

  // Duplicar para loop sin salto
  const frasesDobles = [...frases, ...frases]

  return (
    <div className="bg-defensa border-b border-borde overflow-hidden">
      <div className="flex items-center">
        <div className="bg-defensa px-4 py-2 flex items-center gap-2 border-r border-borde">
          <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
          <span className="font-mono text-xs font-bold text-white uppercase tracking-wide">
            Jugadas Clave
          </span>
        </div>
        <div className="flex-1 overflow-hidden py-2">
          <div className="flex gap-8 cinta whitespace-nowrap font-mono text-sm text-white">
            {frasesDobles.map((frase, i) => (
              <div key={i} className="flex items-center gap-2">
                <span>{frase}</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
