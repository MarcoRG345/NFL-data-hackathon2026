// P3 · Ventaja al lanzar

import { useCallback } from 'react'
import { useApi } from '../hooks/useApi'
import { useTween } from '../hooks/useTween'
import { getVueloResumen } from '../api'
import type { Filtro } from '../types'
import Tarjeta from '../comunes/Tarjeta'
import Insight from '../comunes/Insight'
import EstadoCarga from '../comunes/EstadoCarga'
import { Bar, BarChart, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface Props {
  filtro: Filtro
}

export default function P3Aire({ filtro }: Props) {
  const fetcher = useCallback(() => getVueloResumen(filtro), [filtro])
  const { data, loading, error } = useApi(fetcher)
  const progreso = useTween(1200)

  if (loading || error || !data) {
    return <EstadoCarga loading={loading} error={error} />
  }

  const datosSep = data.por_separacion.map(d => ({
    nombre: d.franja === 'cerrado' ? 'Cerrado\n(<1.5 yd)' : d.franja === 'disputado' ? 'Disputado\n(1.5-3 yd)' : 'Abierto\n(≥3 yd)',
    pct: d.pct_completo !== null && d.pct_completo !== undefined ? d.pct_completo * progreso : null,
    pctReal: d.pct_completo,
    ic_bajo: d.ic?.[0] ?? null,
    ic_alto: d.ic?.[1] ?? null,
    n: d.n,
    color: d.franja === 'cerrado' ? '#F0443A' : d.franja === 'disputado' ? '#F5C542' : '#2ECC85'
  }))

  const datosTend = data.por_tendencia.map(d => ({
    nombre: d.tendencia === 'cerrandose' ? 'Cerrándose' : d.tendencia === 'estable' ? 'Estable' : 'Abriéndose',
    pct: d.pct_completo !== null && d.pct_completo !== undefined ? d.pct_completo * progreso : null,
    pctReal: d.pct_completo,
    ic_bajo: d.ic?.[0] ?? null,
    ic_alto: d.ic?.[1] ?? null,
    n: d.n,
    color: d.tendencia === 'cerrandose' ? '#F0443A' : d.tendencia === 'estable' ? '#F5C542' : '#2ECC85'
  }))

  const hayNullsSep = datosSep.some(d => d.pctReal === null || d.pctReal === undefined)
  const hayNullsTend = datosTend.some(d => d.pctReal === null || d.pctReal === undefined)

  return (
    <div className="aparece space-y-6" key={filtro}>
      <Insight texto={data.insight} />

      <Tarjeta titulo="% Completo por separación al lanzar" subtitulo={`n = ${data.n}`}>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={datosSep} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <XAxis
              dataKey="nombre"
              stroke="#9AA4B2"
              style={{ fontSize: 12 }}
              interval={0}
            />
            <YAxis
              stroke="#9AA4B2"
              style={{ fontSize: 12 }}
              domain={[0, 100]}
              label={{ value: '% Completo', angle: -90, position: 'insideLeft', style: { fill: '#9AA4B2' } }}
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#161B22', border: '1px solid #232A33', borderRadius: 8 }}
              labelStyle={{ color: '#F2F4F7' }}
              itemStyle={{ color: '#F2F4F7' }}
              formatter={(value: any, name: any, props: any) => {
                if (props.payload.pctReal === null || props.payload.pctReal === undefined) {
                  return ['—', `n muy pequeña (n=${props.payload.n})`]
                }
                const ic_bajo = props.payload.ic_bajo
                const ic_alto = props.payload.ic_alto
                const n = props.payload.n
                return [
                  `${(value || 0).toFixed(1)}%`,
                  ic_bajo !== null ? `IC 90%: [${ic_bajo.toFixed(1)}, ${ic_alto.toFixed(1)}], n=${n}` : `n=${n}`
                ]
              }}
            />
            <Bar
              dataKey="pct"
              isAnimationActive={true}
              animationDuration={1200}
              animationEasing="ease-out"
            >
              {datosSep.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.pctReal !== null ? entry.color : '#4A5568'} rx={4} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        {hayNullsSep && (
          <p className="text-tenue text-sm text-center mt-2">
            Nota: "—" indica n muy pequeña para esa franja de separación
          </p>
        )}
      </Tarjeta>

      <Tarjeta titulo="% Completo por tendencia al lanzar" subtitulo={`n = ${data.n}`}>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={datosTend} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <XAxis
              dataKey="nombre"
              stroke="#9AA4B2"
              style={{ fontSize: 12 }}
            />
            <YAxis
              stroke="#9AA4B2"
              style={{ fontSize: 12 }}
              domain={[0, 100]}
              label={{ value: '% Completo', angle: -90, position: 'insideLeft', style: { fill: '#9AA4B2' } }}
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#161B22', border: '1px solid #232A33', borderRadius: 8 }}
              labelStyle={{ color: '#F2F4F7' }}
              itemStyle={{ color: '#F2F4F7' }}
              formatter={(value: any, name: any, props: any) => {
                if (props.payload.pctReal === null || props.payload.pctReal === undefined) {
                  return ['—', `n muy pequeña (n=${props.payload.n})`]
                }
                const ic_bajo = props.payload.ic_bajo
                const ic_alto = props.payload.ic_alto
                const n = props.payload.n
                return [
                  `${(value || 0).toFixed(1)}%`,
                  ic_bajo !== null ? `IC 90%: [${ic_bajo.toFixed(1)}, ${ic_alto.toFixed(1)}], n=${n}` : `n=${n}`
                ]
              }}
            />
            <Bar
              dataKey="pct"
              isAnimationActive={true}
              animationDuration={1200}
              animationEasing="ease-out"
            >
              {datosTend.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.pctReal !== null ? entry.color : '#4A5568'} rx={4} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        {hayNullsTend && (
          <p className="text-tenue text-sm text-center mt-2">
            Nota: "—" indica n muy pequeña para esa tendencia
          </p>
        )}
      </Tarjeta>

      {data.n_aproximado > 0 && (
        <p className="text-tenue text-sm text-center">
          Nota: {data.n_aproximado} objetivos identificados por aproximación (receptor más cercano al balón)
        </p>
      )}
    </div>
  )
}
