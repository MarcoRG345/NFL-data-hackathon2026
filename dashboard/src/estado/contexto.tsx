// Contexto global: sección activa, filtro, vista, equipo

import { createContext, useContext, useState, ReactNode } from 'react'
import type { Filtro, Vista } from '../types'

interface Estado {
  seccion: string
  filtro: Filtro
  vista: Vista
  equipo?: string
}

interface Contexto extends Estado {
  setSeccion: (s: string) => void
  setFiltro: (f: Filtro) => void
  setVista: (v: Vista) => void
  setEquipo: (e?: string) => void
}

const EstadoContexto = createContext<Contexto | null>(null)

export function ProveedorEstado({ children }: { children: ReactNode }) {
  const [estado, setEstado] = useState<Estado>({
    seccion: 'resumen',
    filtro: 'decisivo',
    vista: 'ofe'
  })

  return (
    <EstadoContexto.Provider
      value={{
        ...estado,
        setSeccion: (seccion: string) => setEstado(e => ({ ...e, seccion })),
        setFiltro: (filtro: Filtro) => setEstado(e => ({ ...e, filtro })),
        setVista: (vista: Vista) => setEstado(e => ({ ...e, vista })),
        setEquipo: (equipo?: string) => setEstado(e => ({ ...e, equipo }))
      }}
    >
      {children}
    </EstadoContexto.Provider>
  )
}

export function useEstado() {
  const ctx = useContext(EstadoContexto)
  if (!ctx) throw new Error('useEstado debe usarse dentro de ProveedorEstado')
  return ctx
}
