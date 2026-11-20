// P1 · La carrera de los dos relojes

import { useCallback } from 'react'
import { useApi } from '../hooks/useApi'
import { useTween } from '../hooks/useTween'
import { getCarreraCurvas, getCarreraResultado } from '../api'
import type { Filtro } from '../types'
import Tarjeta from '../comunes/Tarjeta'
import Insight from '../comunes/Insight'
import EstadoCarga from '../comunes/EstadoCarga'
import { ComposedChart, Line, Area, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts'

interface Props {
  filtro: Filtro
}

export default function P1DosRelojes({ filtro }: Props) {
  const fetcherCurvas = useCallback(() => getCarreraCurvas(filtro), [filtro])
  const fetcherResultado = useCallback(() => getCarreraResultado(filtro), [filtro])
  
  const { data: curvas, loading: loadingC, error: errorC } = useApi(fetcherCurvas)
  const { data: resultado, loading: loadingR, error: errorR } = useApi(fetcherResultado)
  const progreso = useTween(1500)

  if (loadingC || loadingR || errorC || errorR || !curvas || !resultado) {
    return <EstadoCarga loading={loadingC || loadingR} error={errorC || errorR} />
  }

  // Verificar valores null en medianas
  const medianaLibreStr = curvas.mediana_libre !== null && curvas.mediana_libre !== undefined
    ? `${curvas.mediana_libre.toFixed(1)}s`
    : '—'
  const medianaPresionStr = curvas.mediana_presion !== null && curvas.mediana_presion !== undefined
    ? `${curvas.mediana_presion.toFixed(1)}s`
    : '—'
  const ventajaStr = curvas.ventaja !== null && curvas.ventaja !== undefined
    ? `${curvas.ventaja.toFixed(1)}s`
    : '—'

  // Insight construido
  const insight = resultado.pct_gana_receptor !== null && curvas.ventaja !== null
    ? `El receptor llega primero en ${resultado.pct_gana_receptor.toFixed(0)}% de jugadas decisivas, con ventaja de ${ventajaStr} (mediana ${medianaLibreStr} vs ${medianaPresionStr}).`
    : 'Análisis de la carrera de los dos relojes en jugadas decisivas.'

  // Datos para las curvas con animación
  const datosCurvas = curvas.puntos.map(p => ({
    t: p.t,
    receptor: p.pct_libre * progreso,
    defensa: p.pct_presion * progreso
  }))

  const hayNullsMedianas = curvas.mediana_libre === null || curvas.mediana_presion === null

  return (
    <div className="aparece space-y-6" key={filtro}>
      <Insight texto={insight} />

      <Tarjeta titulo="La carrera, segundo a segundo" subtitulo={`% de jugadas con receptor libre y presión según tiempo desde el snap (n = ${curvas.n})`}>
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={datosCurvas} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <XAxis
              dataKey="t"
              stroke="#9AA4B2"
              style={{ fontSize: 12 }}
              label={{ value: 'Tiempo desde snap (s)', position: 'insideBottom', offset: -10, style: { fill: '#9AA4B2' } }}
            />
            <YAxis
              stroke="#9AA4B2"
              style={{ fontSize: 12 }}
              domain={[0, 100]}
              label={{ value: '% de jugadas', angle: -90, position: 'insideLeft', style: { fill: '#9AA4B2' } }}
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#161B22', border: '1px solid #232A33', borderRadius: 8 }}
              labelStyle={{ color: '#F2F4F7' }}
              itemStyle={{ color: '#F2F4F7' }}
              formatter={(value: any) => `${(value || 0).toFixed(1)}%`}
            />
            <Legend wrapperStyle={{ paddingTop: 20 }} />
            {curvas.mediana_libre !== null && curvas.mediana_libre !== undefined && (
              <ReferenceLine
                x={curvas.mediana_libre}
                stroke="#2ECC85"
                strokeDasharray="3 3"
                label={{ value: `Mediana libre: ${medianaLibreStr}`, fill: '#2ECC85', position: 'top' }}
              />
            )}
            {curvas.mediana_presion !== null && curvas.mediana_presion !== undefined && (
              <ReferenceLine
                x={curvas.mediana_presion}
                stroke="#F0443A"
                strokeDasharray="3 3"
                label={{ value: `Mediana presión: ${medianaPresionStr}`, fill: '#F0443A', position: 'top' }}
              />
            )}
            <Area
              type="monotone"
              dataKey="receptor"
              fill="#2ECC85"
              fillOpacity={0.2}
              stroke="none"
              isAnimationActive={true}
              animationDuration={1500}
              animationEasing="ease-out"
            />
            <Line
              type="monotone"
              dataKey="receptor"
              stroke="#2ECC85"
              strokeWidth={3}
              dot={false}
              name="Receptor libre"
              isAnimationActive={true}
              animationDuration={1500}
              animationEasing="ease-out"
            />
            <Line
              type="monotone"
              dataKey="defensa"
              stroke="#F0443A"
              strokeWidth={3}
              dot={false}
              name="Presión"
              isAnimationActive={true}
              animationDuration={1500}
              animationEasing="ease-out"
            />
          </ComposedChart>
        </ResponsiveContainer>
        {hayNullsMedianas && (
          <p className="text-tenue text-sm text-center mt-2">
            Nota: "—" indica que no se alcanza ese evento
          </p>
        )}
      </Tarjeta>

      <Tarjeta titulo="Resultado de la carrera" subtitulo={`n = ${resultado.n}`}>
        <div className="space-y-4">
          <div className="h-16 flex rounded-lg overflow-hidden">
            {resultado.pct_gana_receptor !== null && resultado.pct_gana_receptor !== undefined ? (
              <div
                className="bg-receptor flex items-center justify-center font-semibold transition-all duration-1000"
                style={{ width: `${resultado.pct_gana_receptor * progreso}%` }}
              >
                {resultado.pct_gana_receptor > 10 && (
                  <span className="text-white">
                    Gana receptor {resultado.pct_gana_receptor.toFixed(1)}%
                  </span>
                )}
              </div>
            ) : (
              <div className="bg-tenue/30 flex items-center justify-center font-semibold flex-1">
                <span className="text-tenue">Gana receptor —</span>
              </div>
            )}
            {resultado.pct_gana_defensa !== null && resultado.pct_gana_defensa !== undefined ? (
              <div
                className="bg-defensa flex items-center justify-center font-semibold transition-all duration-1000"
                style={{ width: `${resultado.pct_gana_defensa * progreso}%` }}
              >
                {resultado.pct_gana_defensa > 10 && (
                  <span className="text-white">
                    Gana defensa {resultado.pct_gana_defensa.toFixed(1)}%
                  </span>
                )}
              </div>
            ) : (
              <div className="bg-tenue/30 flex items-center justify-center font-semibold flex-1">
                <span className="text-tenue">Gana defensa —</span>
              </div>
            )}
            {resultado.pct_sin_presion !== null && resultado.pct_sin_presion !== undefined ? (
              <div
                className="bg-sinpresion flex items-center justify-center font-semibold transition-all duration-1000"
                style={{ width: `${resultado.pct_sin_presion * progreso}%` }}
              >
                {resultado.pct_sin_presion > 10 && (
                  <span className="text-white">
                    Sin presión {resultado.pct_sin_presion.toFixed(1)}%
                  </span>
                )}
              </div>
            ) : (
              <div className="bg-tenue/30 flex items-center justify-center font-semibold flex-1">
                <span className="text-tenue">Sin presión —</span>
              </div>
            )}
          </div>
          {resultado.pct_sack_con_libre !== null && resultado.pct_sack_con_libre !== undefined ? (
            <p className="text-tenue text-sm text-center">
              {resultado.pct_sack_con_libre.toFixed(1)}% de los sacks ocurrieron con al menos un receptor libre
            </p>
          ) : (
            <p className="text-tenue text-sm text-center">
              Sacks con receptor libre: — (n muy pequeña)
            </p>
          )}
        </div>
      </Tarjeta>

      {/* Visualización de jugadas */}
      <VisualizadorJugadas />
    </div>
  )
}

// Componente para visualizar jugadas de ejemplo
import { useState } from 'react'
import { getJugadasEjemplo, getJugada } from '../api'
import CanchaJugada from '../componentes/CanchaJugada'
import type { EjemploJugada, JugadaResp } from '../types'

function VisualizadorJugadas() {
  const [ejemplos, setEjemplos] = useState<EjemploJugada[] | null>(null)
  const [jugadaSeleccionada, setJugadaSeleccionada] = useState<string | null>(null)
  const [jugada, setJugada] = useState<JugadaResp | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Cargar ejemplos al montar
  useState(() => {
    getJugadasEjemplo()
      .then(setEjemplos)
      .catch(() => setError('Error al cargar ejemplos'))
  })

  const cargarJugada = async (ejemplo: EjemploJugada) => {
    setLoading(true)
    setError(null)
    setJugadaSeleccionada(ejemplo.id)
    try {
      const data = await getJugada(ejemplo.gameId, ejemplo.playId)
      setJugada(data)
    } catch {
      setError('Error al cargar jugada')
    } finally {
      setLoading(false)
    }
  }

  if (error && !ejemplos) {
    return <EstadoCarga loading={false} error={error} />
  }

  if (!ejemplos || ejemplos.length === 0) {
    return null
  }

  return (
    <Tarjeta titulo="Visualización de jugadas" subtitulo="Selecciona una jugada para ver la animación">
      <div className="space-y-4">
        {/* Selector de jugadas */}
        <div className="flex gap-2">
          {ejemplos.map((ej) => (
            <button
              key={ej.id}
              onClick={() => cargarJugada(ej)}
              className={`px-4 py-2 rounded transition-colors ${
                jugadaSeleccionada === ej.id
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 hover:bg-gray-300 text-gray-800'
              }`}
            >
              {ej.titulo}
            </button>
          ))}
        </div>

        {/* Visualización */}
        {loading && <EstadoCarga loading={true} error={null} />}
        {error && jugadaSeleccionada && <EstadoCarga loading={false} error={error} />}
        {jugada && !loading && <CanchaJugada jugada={jugada} />}
      </div>
    </Tarjeta>
  )
}
