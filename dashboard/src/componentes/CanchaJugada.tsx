import { useState, useEffect } from 'react';
import type { JugadaResp, CuadroJugada, JugadorCuadro } from '../types';

interface CanchaJugadaProps {
  jugada: JugadaResp;
}

const COLORES_ROL = {
  qb: '#3b82f6',
  receptor: '#10b981',
  defensor: '#ef4444',
  rusher: '#f59e0b',
  otro: '#6b7280',
};

export default function CanchaJugada({ jugada }: CanchaJugadaProps) {
  const [frameActual, setFrameActual] = useState(0);
  const [reproduciendo, setReproduciendo] = useState(false);

  const cuadroActual = jugada.cuadros[frameActual];

  useEffect(() => {
    if (!reproduciendo) return;

    const intervalo = setInterval(() => {
      setFrameActual((prev) => {
        if (prev >= jugada.cuadros.length - 1) {
          setReproduciendo(false);
          return prev;
        }
        return prev + 1;
      });
    }, 100);

    return () => clearInterval(intervalo);
  }, [reproduciendo, jugada.cuadros.length]);

  const toggleReproducir = () => {
    if (frameActual >= jugada.cuadros.length - 1) {
      setFrameActual(0);
    }
    setReproduciendo(!reproduciendo);
  };

  const reiniciar = () => {
    setFrameActual(0);
    setReproduciendo(false);
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="mb-4">
        <h3 className="font-semibold text-lg mb-2">{jugada.contexto.descripcion}</h3>
        <div className="text-sm text-gray-600">
          {jugada.contexto.down}º & {jugada.contexto.yardsToGo} | Q{jugada.contexto.cuarto} {jugada.contexto.reloj} | {jugada.contexto.marcador_texto}
        </div>
      </div>

      <svg viewBox="0 0 600 300" className="w-full border border-gray-300 bg-green-50">
        {Array.from({ length: 11 }, (_, i) => {
          const x = 50 + i * 50;
          return (
            <g key={i}>
              <line x1={x} y1={0} x2={x} y2={300} stroke="#ddd" strokeWidth="1" />
              <text x={x} y={15} textAnchor="middle" fontSize="10" fill="#666">{i * 10}</text>
            </g>
          );
        })}
        <ellipse cx={cuadroActual.balon.x * 5 + 50} cy={cuadroActual.balon.y * 5 + 50} rx="8" ry="4" fill="#8b4513" stroke="#000" strokeWidth="1" />
        {cuadroActual.jugadores.map((jugador: JugadorCuadro) => {
          const x = jugador.x * 5 + 50;
          const y = jugador.y * 5 + 50;
          const color = COLORES_ROL[jugador.rol];
          return (
            <g key={jugador.nflId}>
              <circle cx={x} cy={y} r="10" fill={color} stroke={jugador.girando ? '#fbbf24' : '#000'} strokeWidth={jugador.girando ? '3' : '1'} opacity="0.8" />
              {jugador.jersey && <text x={x} y={y + 4} textAnchor="middle" fontSize="10" fontWeight="bold" fill="#fff">{jugador.jersey}</text>}
            </g>
          );
        })}
      </svg>

      <div className="mt-4 space-y-3">
        <input type="range" min="0" max={jugada.cuadros.length - 1} value={frameActual} onChange={(e) => { setFrameActual(parseInt(e.target.value)); setReproduciendo(false); }} className="w-full" />
        <div className="flex gap-2">
          <button onClick={toggleReproducir} className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
            {reproduciendo ? 'Pausar' : 'Reproducir'}
          </button>
          <button onClick={reiniciar} className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600">Reiniciar</button>
        </div>
      </div>
    </div>
  );
}
