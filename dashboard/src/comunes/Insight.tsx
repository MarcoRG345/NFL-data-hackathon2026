// Insight: franja con borde izquierdo de acento y frase destacada

interface Props {
  texto: string
}

export default function Insight({ texto }: Props) {
  return (
    <div className="border-l-4 border-acento bg-panel pl-6 pr-4 py-4 rounded-r-lg mb-6">
      <p className="text-texto text-lg leading-relaxed font-medium">{texto}</p>
    </div>
  )
}
