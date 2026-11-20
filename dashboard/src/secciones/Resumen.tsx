// Resumen

import { useCallback } from 'react'
import { useApi } from '../hooks/useApi'
import { getResumen } from '../api'
import type { Filtro, Vista } from '../types'
import Tarjeta from '../comunes/Tarjeta'
import Kpi from '../comunes/Kpi'
import Insight from '../comunes/Insight'
import EstadoCarga from '../comunes/EstadoCarga'

interface Props {
  filtro: Filtro
  vista: Vista
  equipo?: string
}

function formatValor(valor: number | null | undefined, unidad: string = '%'): string {
  if (valor === null || valor === undefined) return '—'
  return `${valor.toFixed(1)}${unidad}`
}

export default function Resumen({ filtro, vista, equipo }: Props) {
  const fetcher = useCallback(() => getResumen(filtro, vista, equipo), [filtro, vista, equipo])
  const { data, loading, error } = useApi(fetcher)

  if (loading || error || !data) {
    return <EstadoCarga loading={loading} error={error} />
  }

  const hayNulls = data.cadena_liga.some(p => p.pct === null || p.pct === undefined)

  return (
    <div className="aparece space-y-6" key={`${filtro}-${vista}-${equipo}`}>
      <Insight texto={data.insight} />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Tarjeta>
          {data.kpis.pct_gana_receptor !== null && data.kpis.pct_gana_receptor !== undefined ? (
            <Kpi valor={data.kpis.pct_gana_receptor} etiqueta="Gana receptor" unidad="%" color="text-receptor" />
          ) : (
            <div className="text-center">
              <div className="font-titulo text-5xl font-extrabold text-tenue">—</div>
              <div className="text-tenue text-sm mt-2 uppercase tracking-wide">Gana receptor</div>
              <div className="text-tenue text-xs mt-1">n muy pequeña</div>
            </div>
          )}
        </Tarjeta>
        <Tarjeta>
          {data.kpis.pct_gana_defensa !== null && data.kpis.pct_gana_defensa !== undefined ? (
            <Kpi valor={data.kpis.pct_gana_defensa} etiqueta="Gana defensa" unidad="%" color="text-defensa" />
          ) : (
            <div className="text-center">
              <div className="font-titulo text-5xl font-extrabold text-tenue">—</div>
              <div className="text-tenue text-sm mt-2 uppercase tracking-wide">Gana defensa</div>
              <div className="text-tenue text-xs mt-1">n muy pequeña</div>
            </div>
          )}
        </Tarjeta>
        <Tarjeta>
          {data.kpis.conv_gana_receptor !== null && data.kpis.conv_gana_receptor !== undefined ? (
            <Kpi valor={data.kpis.conv_gana_receptor} etiqueta="Conv. gana receptor" unidad="%" color="text-receptor" />
          ) : (
            <div className="text-center">
              <div className="font-titulo text-5xl font-extrabold text-tenue">—</div>
              <div className="text-tenue text-sm mt-2 uppercase tracking-wide">Conv. gana receptor</div>
              <div className="text-tenue text-xs mt-1">n muy pequeña</div>
            </div>
          )}
        </Tarjeta>
        <Tarjeta>
          {data.kpis.conv_gana_defensa !== null && data.kpis.conv_gana_defensa !== undefined ? (
            <Kpi valor={data.kpis.conv_gana_defensa} etiqueta="Conv. gana defensa" unidad="%" color="text-defensa" />
          ) : (
            <div className="text-center">
              <div className="font-titulo text-5xl font-extrabold text-tenue">—</div>
              <div className="text-tenue text-sm mt-2 uppercase tracking-wide">Conv. gana defensa</div>
              <div className="text-tenue text-xs mt-1">n muy pequeña</div>
            </div>
          )}
        </Tarjeta>
      </div>

      <Tarjeta titulo="La cadena de la liga" subtitulo={`Tasas condicionales: cada paso sobre los que pasaron el anterior (n = ${data.n})`}>
        <div className="space-y-4">
          {data.cadena_liga.map((paso, i) => {
            const esPendiente = paso.pct === null || paso.pct === undefined
            return (
              <div key={i}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-texto font-medium">{paso.paso}</span>
                  <span className="text-texto font-bold">
                    {esPendiente ? '—' : `${paso.pct.toFixed(1)}%`}
                  </span>
                </div>
                <div className="h-3 bg-panel rounded-full overflow-hidden">
                  {!esPendiente && (
                    <div
                      className="h-full bg-receptor rounded-full transition-all duration-1000"
                      style={{ width: `${paso.pct}%` }}
                    />
                  )}
                  {esPendiente && (
                    <div className="h-full bg-tenue/30 rounded-full" />
                  )}
                </div>
              </div>
            )
          })}
        </div>
        {hayNulls && (
          <p className="text-tenue text-sm mt-4">
            Nota: "—" indica que no se alcanza ese paso o que la n es muy pequeña
          </p>
        )}
        <div className="mt-6 flex items-center gap-3 text-texto flex-wrap">
          <span className="text-receptor font-semibold">Se libera</span>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-tenue">
            <path d="M5 12h14M12 5l7 7-7 7" />
          </svg>
          <span className="text-receptor font-semibold">Gana la carrera</span>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-tenue">
            <path d="M5 12h14M12 5l7 7-7 7" />
          </svg>
          <span className="text-receptor font-semibold">Abierto al lanzar</span>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-tenue">
            <path d="M5 12h14M12 5l7 7-7 7" />
          </svg>
          <span className="text-receptor font-semibold">Completa</span>
        </div>
      </Tarjeta>
    </div>
  )
}
