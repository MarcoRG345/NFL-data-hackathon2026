// Tarjeta común: fondo tarjeta, borde, radio y padding estándar

interface Props {
  titulo?: string
  subtitulo?: string
  children: React.ReactNode
}

export default function Tarjeta({ titulo, subtitulo, children }: Props) {
  return (
    <div className="bg-tarjeta border border-borde rounded-2xl p-6">
      {titulo && (
        <div className="mb-4">
          <h3 className="font-titulo text-2xl font-bold tracking-wide uppercase text-texto">
            {titulo}
          </h3>
          {subtitulo && <p className="text-sm text-tenue mt-1">{subtitulo}</p>}
        </div>
      )}
      {children}
    </div>
  )
}
