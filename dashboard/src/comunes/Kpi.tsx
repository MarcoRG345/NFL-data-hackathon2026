// KPI: número grande animado con etiqueta

import { useTween } from '../hooks/useTween'

interface Props {
  valor: number
  etiqueta: string
  unidad?: string
  decimales?: number
  color?: string
}

export default function Kpi({ valor, etiqueta, unidad = '', decimales = 1, color = 'text-acento' }: Props) {
  const progreso = useTween(900)
  const actual = valor * progreso

  return (
    <div className="text-center">
      <div className={`font-titulo text-5xl font-extrabold ${color}`}>
        {actual.toFixed(decimales)}
        {unidad && <span className="text-3xl ml-1">{unidad}</span>}
      </div>
      <div className="text-tenue text-sm mt-2 uppercase tracking-wide">{etiqueta}</div>
    </div>
  )
}
