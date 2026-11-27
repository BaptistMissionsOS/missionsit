// This source code is freely given for the sake of the gospel (Matthew 10:8)
// and is licensed under MIT No Attribution (MIT-0).

import frappeUIPreset, { content as frappeUIContent } from 'frappe-ui/tailwind'

/** @type {import('tailwindcss').Config} */
export default {
  presets: [frappeUIPreset],
  content: ['./index.html', './src/**/*.{vue,js,ts}', ...frappeUIContent],
  theme: {
    extend: {
      colors: {
        // "Departures": ink for the board and headings, airmail blue for the way in,
        // harvest gold only where someone gives.
        ink: { DEFAULT: '#14213D', soft: '#2A3858' },
        airmail: { DEFAULT: '#2D4E9C', dark: '#223D7E', tint: '#E8EDF7' },
        harvest: { DEFAULT: '#C9962B', dark: '#A97C1F', tint: '#FBF3E2' },
        sage: { DEFAULT: '#3E7A5C', tint: '#E6F1EB' },
        mist: '#F3F5F9',
      },
      fontFamily: {
        display: ['"Bricolage Grotesque Variable"', 'Inter', 'system-ui', 'sans-serif'],
      },
      maxWidth: { page: '72rem' },
    },
  },
}
