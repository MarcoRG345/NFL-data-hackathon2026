// Tipos desde contrato-api.md

export type Filtro = 'decisivo' | 'pocas_yardas' | 'reloj_final' | 'marcador_cerrado' | 'normal'
export type Vista = 'ofe' | 'def'
export type Modo = 'decisivo' | 'normal'

export interface EstadoDatos {
  listo: boolean
  cargando: boolean
  error: string | null
  semanas: number
  n_jugadas: number
}

export interface KPIs {
  pct_gana_receptor: number
  pct_gana_defensa: number
  conv_gana_receptor: number
  conv_gana_defensa: number
  reloj_defensa_mediana: number
  conv_equipo: number
  eslabon_equipo: string
}

export interface PasoCadena {
  paso: string
  pct: number
}

export interface Resumen {
  filtro: Filtro
  vista: Vista
  n: number
  kpis: KPIs
  cadena_liga: PasoCadena[]
  insight: string
}

export interface PorSeparacion {
  franja: 'cerrado' | 'disputado' | 'abierto'
  n: number
  pct_completo: number
  ic: [number, number] | null
}

export interface PorTendencia {
  tendencia: 'cerrandose' | 'estable' | 'abriendose'
  n: number
  pct_completo: number
  ic: [number, number] | null
}

export interface VueloResumen {
  filtro: Filtro
  n: number
  n_aproximado: number
  por_separacion: PorSeparacion[]
  por_tendencia: PorTendencia[]
  insight: string
}

export interface PorTipoGiro {
  franja: 'corta' | 'media' | 'larga'
  tipo: 'sin_giro' | 'suave' | 'brusco'
  n: number
  sep_ganada: number
  ic: [number, number] | null
}

export interface GirosResumen {
  filtro: Filtro
  n: number
  por_tipo: PorTipoGiro[]
  insight: string
}

export interface PuntoCurva {
  t: number
  pct_libre: number
  pct_presion: number
}

export interface CarreraCurvas {
  filtro: Filtro
  n: number
  puntos: PuntoCurva[]
  mediana_libre: number
  mediana_presion: number
  ventaja: number
}

export interface CarreraResultado {
  filtro: Filtro
  n: number
  pct_gana_receptor: number
  pct_gana_defensa: number
  pct_sin_presion: number
  pct_sack_con_libre: number
}

// Tipos para visualización de jugadas
export interface EjemploJugada {
  id: string
  gameId: number
  playId: number
  titulo: string
  ganador: 'receptor' | 'defensa'
  situacion: string
}

export interface ContextoJugada {
  down: number
  yardsToGo: number
  cuarto: number
  reloj: string
  marcador_texto: string
  descripcion: string
  resultado: string
}

export interface RelojesJugada {
  t_presion: number | null
  t_libre: number | null
  ganador: 'receptor' | 'defensa' | 'sin_presion'
  margen: number | null
}

export interface BalonJugada {
  t_lanza: number
  t_llega: number
  x_lanza: number
  y_lanza: number
  x_llega: number
  y_llega: number
}

export interface EventoJugada {
  t: number
  nombre: string
}

export interface BalonCuadro {
  x: number
  y: number
  altura: number
}

export interface JugadorCuadro {
  nflId: number
  x: number
  y: number
  s: number
  dir: number
  giro_grados: number
  girando: boolean
  lado: 'ataque' | 'defensa'
  jersey: number | null
  posicion: string
  rol: 'qb' | 'receptor' | 'defensor' | 'rusher' | 'otro'
}

export interface CuadroJugada {
  t: number
  separacion: number | null
  receptor_libre: boolean
  presion_llego: boolean
  balon: BalonCuadro
  jugadores: JugadorCuadro[]
}

export interface JugadaResp {
  contexto: ContextoJugada
  linea_golpeo: number
  linea_primer_down: number
  relojes: RelojesJugada
  balon: BalonJugada
  eventos: EventoJugada[]
  cuadros: CuadroJugada[]
}
