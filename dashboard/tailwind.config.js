/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        fondo: '#0D1015',
        panel: '#11151B',
        tarjeta: '#161B22',
        borde: '#232A33',
        texto: '#F2F4F7',
        tenue: '#9AA4B2',
        acento: '#FF6B1A',
        receptor: '#2ECC85',
        defensa: '#F0443A',
        sinpresion: '#3B9EE8',
        balon: '#F5C542'
      },
      fontFamily: {
        titulo: ['"Barlow Condensed"', '"Arial Narrow"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif']
      }
    }
  },
  plugins: []
}
