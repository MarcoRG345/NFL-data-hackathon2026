// Menú lateral: logo, selector de vista, lista de secciones

import { useEstado } from '../estado/contexto'

interface Seccion {
  id: string
  label: string
  visible: boolean
}

const SECCIONES: Seccion[] = [
  { id: 'resumen', label: 'Resumen', visible: true },
  { id: 'p1', label: 'P1 · Dos relojes', visible: true },
  { id: 'p2', label: 'P2 · El giro', visible: true },
  { id: 'p3', label: 'P3 · Ventaja al lanzar', visible: true },
  { id: 'como-leer', label: 'Cómo leer esto', visible: true }
]

export default function Sidebar() {
  const { seccion, vista, setSeccion, setVista } = useEstado()

  return (
    <aside className="bg-panel border-r border-borde w-64 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-borde">
        <div className="font-titulo text-xl font-extrabold tracking-wider text-acento">
          2C · TWO CLOCKS
        </div>
        <div className="text-tenue text-xs mt-1 uppercase tracking-wide">Scout Analytics</div>
      </div>

      {/* Selector de vista */}
      <div className="p-4 border-b border-borde">
        <div className="text-tenue text-xs uppercase tracking-wide mb-2">Vista</div>
        <div className="flex gap-2">
          <button
            onClick={() => setVista('ofe')}
            aria-pressed={vista === 'ofe'}
            className={`flex-1 py-2 px-3 text-sm rounded transition-colors ${
              vista === 'ofe'
                ? 'bg-acento text-white font-semibold'
                : 'bg-tarjeta text-tenue hover:bg-borde'
            }`}
          >
            Ofensiva
          </button>
          <button
            onClick={() => setVista('def')}
            aria-pressed={vista === 'def'}
            className={`flex-1 py-2 px-3 text-sm rounded transition-colors ${
              vista === 'def'
                ? 'bg-acento text-white font-semibold'
                : 'bg-tarjeta text-tenue hover:bg-borde'
            }`}
          >
            Defensiva
          </button>
        </div>
      </div>

      {/* Lista de secciones */}
      <nav className="flex-1 p-4">
        <ul className="space-y-1">
          {SECCIONES.filter(s => s.visible).map(s => (
            <li key={s.id}>
              <button
                onClick={() => setSeccion(s.id)}
                aria-current={seccion === s.id ? 'page' : undefined}
                className={`w-full text-left px-4 py-3 rounded transition-colors ${
                  seccion === s.id
                    ? 'bg-tarjeta text-texto font-semibold border-l-4 border-acento'
                    : 'text-tenue hover:bg-tarjeta hover:text-texto'
                }`}
              >
                {s.label}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  )
}
