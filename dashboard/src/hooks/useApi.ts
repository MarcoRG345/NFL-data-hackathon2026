// Hook para llamadas con reintento automático en 503

import { useEffect, useState } from 'react'

interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

export function useApi<T>(fetcher: () => Promise<T>): UseApiState<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: true,
    error: null
  })

  useEffect(() => {
    let mounted = true
    let timer: ReturnType<typeof setTimeout> | null = null

    const load = async () => {
      try {
        const data = await fetcher()
        if (mounted) setState({ data, loading: false, error: null })
      } catch (err) {
        if (mounted) {
          const status = (err as any).message?.startsWith('503')
          if (status) {
            // Reintento en 3s si es 503
            timer = setTimeout(load, 3000)
            setState({ data: null, loading: true, error: 'Cargando datos...' })
          } else {
            setState({ data: null, loading: false, error: (err as Error).message })
          }
        }
      }
    }

    load()

    return () => {
      mounted = false
      if (timer) clearTimeout(timer)
    }
  }, [fetcher])

  return state
}
