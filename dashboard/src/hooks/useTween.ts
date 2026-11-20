// Hook para animaciones: progreso de 0 a 1 con ease-out cúbico

import { useEffect, useState } from 'react'

export function useTween(duracion: number = 900): number {
  const [progreso, setProgreso] = useState(0)

  useEffect(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (prefersReduced) {
      setProgreso(1)
      return
    }

    const inicio = Date.now()
    let animId: number

    const tick = () => {
      const t = Math.min((Date.now() - inicio) / duracion, 1)
      // ease-out cubic: 1 - (1-t)^3
      const ease = 1 - Math.pow(1 - t, 3)
      setProgreso(ease)
      if (t < 1) animId = requestAnimationFrame(tick)
    }

    animId = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(animId)
  }, [duracion])

  return progreso
}
