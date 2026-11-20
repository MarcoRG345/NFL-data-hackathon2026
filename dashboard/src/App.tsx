import { ProveedorEstado, useEstado } from './estado/contexto'
import Ticker from './layout/Ticker'
import Sidebar from './layout/Sidebar'
import Resumen from './secciones/Resumen'
import P1DosRelojes from './secciones/P1DosRelojes'
import P2Giro from './secciones/P2Giro'
import P3Aire from './secciones/P3Aire'
import ComoLeer from './secciones/ComoLeer'

function Contenido() {
  const { seccion, filtro, vista, equipo } = useEstado()

  let contenido = null
  switch (seccion) {
    case 'resumen':
      contenido = <Resumen filtro={filtro} vista={vista} equipo={equipo} />
      break
    case 'p1':
      contenido = <P1DosRelojes filtro={filtro} />
      break
    case 'p2':
      contenido = <P2Giro filtro={filtro} />
      break
    case 'p3':
      contenido = <P3Aire filtro={filtro} />
      break
    case 'como-leer':
      contenido = <ComoLeer />
      break
    default:
      contenido = (
        <div className="text-center py-12 text-tenue">
          <p>Esta sección aún no está disponible.</p>
        </div>
      )
  }

  return (
    <main className="flex-1 p-8 overflow-y-auto">
      {contenido}
    </main>
  )
}

export default function App() {
  return (
    <ProveedorEstado>
      <div className="flex flex-col h-screen">
        <Ticker />
        <div className="flex flex-1 overflow-hidden">
          <Sidebar />
          <Contenido />
        </div>
      </div>
    </ProveedorEstado>
  )
}
