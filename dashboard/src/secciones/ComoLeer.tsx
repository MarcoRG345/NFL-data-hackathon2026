// Cómo leer esto: pregunta, cadena, definiciones, limitaciones y créditos

export default function ComoLeer() {
  return (
    <div className="aparece space-y-6 max-w-4xl">
      <section className="bg-tarjeta border border-borde rounded-2xl p-6">
        <h3 className="font-titulo text-2xl font-bold tracking-wide uppercase text-acento mb-4">
          La pregunta
        </h3>
        <p className="text-texto leading-relaxed text-lg mb-4">
          En los momentos decisivos (3.º y 4.º down), <strong>¿qué llega primero: el receptor libre o la defensa sobre el mariscal?</strong> ¿Y qué hace que el receptor gane esa carrera y llegue abierto al lanzamiento?
        </p>
      </section>

      <section className="bg-tarjeta border border-borde rounded-2xl p-6">
        <h3 className="font-titulo text-2xl font-bold tracking-wide uppercase text-acento mb-4">
          La cadena
        </h3>
        <div className="flex items-center gap-4 text-texto flex-wrap">
          <div className="flex items-center gap-2">
            <span className="text-receptor font-semibold">Se libera</span>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-tenue">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-receptor font-semibold">Gana la carrera</span>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-tenue">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-receptor font-semibold">Abierto al lanzar</span>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-tenue">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </div>
          <span className="text-receptor font-semibold">Completa</span>
        </div>
        <p className="text-tenue text-sm mt-4">
          Cada paso se mide sobre las jugadas que pasaron el anterior. El eslabón débil de un equipo es el paso donde cae más bajo de la mediana de la liga.
        </p>
      </section>

      <section className="bg-tarjeta border border-borde rounded-2xl p-6">
        <h3 className="font-titulo text-2xl font-bold tracking-wide uppercase text-acento mb-4">
          Definiciones clave
        </h3>
        <dl className="space-y-4 text-texto">
          <div>
            <dt className="font-semibold text-receptor">Receptor libre</dt>
            <dd className="text-tenue text-sm ml-4">Separación ≥ 3.0 yardas de su defensor más cercano, contando solo desde 1.0 s después del snap.</dd>
          </div>
          <div>
            <dt className="font-semibold text-defensa">Presión</dt>
            <dd className="text-tenue text-sm ml-4">Un rusher de pase llega a ≤ 2.0 yardas del mariscal antes del lanzamiento, o hubo sack.</dd>
          </div>
          <div>
            <dt className="font-semibold text-balon">Abierto al lanzar</dt>
            <dd className="text-tenue text-sm ml-4">El receptor objetivo tiene ≥ 3.0 yardas de separación cuando sale el balón (pass_forward).</dd>
          </div>
          <div>
            <dt className="font-semibold text-balon">Tendencia</dt>
            <dd className="text-tenue text-sm ml-4">
              <strong>Abriéndose:</strong> ganó más de 0.5 yd en los últimos 0.5 s. 
              <strong>Cerrándose:</strong> perdió más de 0.5 yd. 
              <strong>Estable:</strong> entre ambos.
            </dd>
          </div>
          <div>
            <dt className="font-semibold text-texto">Giro brusco</dt>
            <dd className="text-tenue text-sm ml-4">Cambio de dirección ≥ 60° en 0.5 s, con velocidad ≥ 2 yd/s antes y después.</dd>
          </div>
        </dl>
      </section>

      <section className="bg-tarjeta border border-borde rounded-2xl p-6">
        <h3 className="font-titulo text-2xl font-bold tracking-wide uppercase text-acento mb-4">
          Limitaciones de los datos
        </h3>
        <ul className="space-y-2 text-tenue text-sm list-disc list-inside">
          <li>El tracking termina ~0.5 s después del lanzamiento. No hay cuadros del balón en el aire: no se puede medir separación real a la llegada.</li>
          <li>El receptor objetivo se identifica por nombre en la descripción de la jugada. Si no hay coincidencia única, se usa el receptor más cercano al balón (marcado como aproximado).</li>
          <li>Los porcentajes por objetivo están algo inflados porque el objetivo se identifica mejor en pases completos que en incompletos.</li>
          <li>Solo jugadas de pase. No hay información de cobertura asignada ni de tacleos.</li>
        </ul>
      </section>

      <section className="bg-tarjeta border border-borde rounded-2xl p-6">
        <h3 className="font-titulo text-2xl font-bold tracking-wide uppercase text-acento mb-4">
          Fuente y créditos
        </h3>
        <p className="text-tenue text-sm leading-relaxed">
          Datos del evento regional del Big Data Bowl (temporada 2021 de la NFL: tracking, plays, players y pffScoutingData), 
          entregados por los organizadores del hackathon. 
          Análisis y visualización: Two Clocks · Scout Analytics. 
          Proyecto desarrollado para el hackathon NFL x UNAM 2026.
        </p>
      </section>
    </div>
  )
}
