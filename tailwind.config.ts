import type { Config } from 'tailwindcss'
const config: Config = {
  darkMode: ['class'],
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        border: 'hsl(214, 32%, 22%)',
        background: '#0b0f14',
        panel: '#101723',
        card: '#0f1620',
        primary: '#5cc8ff',
        danger: '#ff6b6b',
        text: '#d8e1ea',
        muted: '#9fb0c2',
      },
      borderRadius: {
        xl: '1rem',
        '2xl': '1.25rem',
      },
    },
  },
  plugins: [],
}
export default config
