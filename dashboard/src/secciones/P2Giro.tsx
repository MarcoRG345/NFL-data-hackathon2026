// P2 · El giro

import { useCallback } from 'react'
import { useApi } from '../hooks/useApi'
import { useTween } from '../hooks/useTween'
import { getGirosResumen } from '../api'
import type { Filtro } from '../types'
import Tarjeta from '../comunes/Tarjeta'
import Insight from '../comunes/Insight'
import EstadoCarga from '../comunes/EstadoCarga'
import { Bar, BarChart, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, LabelList } from 'recharts'

interface Props {
  filtro: Filtro
}

export default function P2Giro({ filtro }: Props) {
  const fetcher = useCallback(() => getGirosResumen(filtro), [filtro])
  const { data, loading, error } = useApi(fetcher)
  const progreso = useTween(1200)

  if (loading || error || !data) {
    return <EstadoCarga loading={loading} error={error} />
  }

  // Datos de separación ganada con manejo de null
  const datosSep = data.por_tipo.map(d => ({
    nombre: d.tipo === 'sin_giro' ? 'Sin giro\n(<30°)' : d.tipo === 'suave' ? 'Suave\n(30-60°)' : 'Brusco\n(≥60°)',
    valor: d.sep_ganada !== null && d.sep_ganada !== undefined ? d.sep_ganada * progreso : null,
    valorReal: d.sep_ganada,
    ic: d.ic,
    n: d.n,
    color: d.tipo === 'sin_giro' ? '#9AA4B2' : d.tipo === 'suave' ? '#F5C542' : '#FF6B1A',
    etiqueta: d.sep_ganada !== null && d.sep_ganada !== undefined
      ? `${d.sep_ganada >= 0 ? '+' : ''}${d.sep_ganada.toFixed(2)} yd`
      : '—'
  }))

  const hayNulls = datosSep.some(d => d.valorReal === null || d.valorReal === undefined)

  return (
    <div className="aparece space-y-6" key={filtro}>
      <Insight texto={data.insight} />

      <Tarjeta titulo="Separación ganada por tipo de giro" subtitulo={`Separación ganada en 0.5 s después del giro (n = ${data.n})`}>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={datosSep} margin={{ top: 40, right: 20, bottom: 20, left: 40 }}>
            <XAxis
              dataKey="nombre"
              stroke="#9AA4B2"
              style={{ fontSize: 12 }}
              interval={0}
            />
            <YAxis
              stroke="#9AA4B2"
              style={{ fontSize: 12 }}
              label={{ value: 'Separación ganada (yd)', angle: -90, position: 'insideLeft', style: { fill: '#9AA4B2' } }}
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#161B22', border: '1px solid #232A33', borderRadius: 8 }}
              labelStyle={{ color: '#F2F4F7' }}
              itemStyle={{ color: '#F2F4F7' }}
              formatter={(value: any, name: any, props: any) => {
                if (props.payload.valorReal === null || props.payload.valorReal === undefined) {
                  return ['—', `n muy pequeña (n=${props.payload.n})`]
                }
                const ic = props.payload.ic
                const n = props.payload.n
                return [
                  `${(value || 0).toFixed(1)} yd`,
                  ic ? `IC 90%: [${ic[0].toFixed(1)}, ${ic[1].toFixed(1)}], n=${n}` : `n=${n}`
                ]
              }}
            />
            <Bar
              dataKey="valor"
              isAnimationActive={true}
              animationDuration={1200}
              animationEasing="ease-out"
            >
              {datosSep.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.valorReal !== null ? entry.color : '#4A5568'} rx={4} />
              ))}
              <LabelList
                dataKey="etiqueta"
                position="top"
                style={{ fill: '#F2F4F7', fontSize: 12, fontWeight: 600 }}
                content={(props: any) => {
                  const { x, y, width, value, index } = props
                  const entry = datosSep[index]
                  if (!entry) return null
                  return (
                    <text
                      x={x + width / 2}
                      y={y - 10}
                      fill="#F2F4F7"
                      fontSize={12}
                      fontWeight={600}
                      textAnchor="middle"
                    >
                      <tspan x={x + width / 2} dy="0">{value}</tspan>
                      <tspan x={x + width / 2} dy="14">n={entry.n}</tspan>
                    </text>
                  )
                }}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        {hayNulls && (
          <p className="text-tenue text-sm text-center mt-2">
            Nota: "—" indica n muy pequeña para ese tipo de giro
          </p>
        )}
      </Tarjeta>
    </div>
  )
}


