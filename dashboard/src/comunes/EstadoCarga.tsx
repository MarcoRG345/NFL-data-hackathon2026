// Estados de carga, error y sin datos

interface Props {
  loading?: boolean
  error?: string | null
  sinDatos?: boolean
  n?: number
  children?: React.ReactNode
}

export default function EstadoCarga({ loading, error, sinDatos, n, children }: Props) {
  if (loading) {
    return (
      <div className="space-y-4">
        {/* Esqueleto de carga */}
        <div className="h-8 bg-panel rounded animate-pulse" />
        <div className="h-64 bg-panel rounded animate-pulse" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-defensa/10 border border-defensa rounded-lg p-6 text-center">
        <p className="text-defensa font-medium mb-2">Error al cargar</p>
        <p className="text-tenue text-sm">{error}</p>
      </div>
    )
  }

  if (sinDatos && n !== undefined && n < 20) {
    return (
      <div className="bg-panel border border-borde rounded-lg p-6 text-center">
        <p className="text-tenue">Muy pocas jugadas para este filtro (n = {n})</p>
      </div>
    )
  }

  return <>{children}</>
}
