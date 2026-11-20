// Funciones de llamada a la API. fetch('api/...') sin diagonal inicial.

import type { EstadoDatos, Resumen, VueloResumen, GirosResumen, CarreraCurvas, CarreraResultado, Filtro, Vista } from './types'

const BASE = 'api/'

async function fetchApi<T>(endpoint: string): Promise<T> {
  const res = await fetch(BASE + endpoint)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

export async function getEstadoDatos(): Promise<EstadoDatos> {
  return fetchApi<EstadoDatos>('estado-datos')
}

export async function getResumen(filtro: Filtro, vista: Vista, equipo?: string): Promise<Resumen> {
  const params = new URLSearchParams({ filtro, vista })
  if (equipo) params.set('equipo', equipo)
  return fetchApi<Resumen>('resumen?' + params)
}

export async function getVueloResumen(filtro: Filtro): Promise<VueloResumen> {
  return fetchApi<VueloResumen>('vuelo/resumen?filtro=' + filtro)
}

export async function getGirosResumen(filtro: Filtro): Promise<GirosResumen> {
  return fetchApi<GirosResumen>('giros/resumen?filtro=' + filtro)
}

export async function getCarreraCurvas(filtro: Filtro): Promise<CarreraCurvas> {
  return fetchApi<CarreraCurvas>('carrera/curvas?filtro=' + filtro)
}

export async function getCarreraResultado(filtro: Filtro): Promise<CarreraResultado> {
  return fetchApi<CarreraResultado>('carrera/resultado?filtro=' + filtro)
}

export async function getJugadasEjemplo(): Promise<import('./types').EjemploJugada[]> {
  return fetchApi<import('./types').EjemploJugada[]>('jugadas-ejemplo')
}

export async function getJugada(gameId: number, playId: number): Promise<import('./types').JugadaResp> {
  return fetchApi<import('./types').JugadaResp>(`jugada?gameId=${gameId}&playId=${playId}`)
}
