/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        'primary-blue': '#1e40af',
        'primary-blue-light': '#3b82f6',
        'primary-blue-dark': '#1e3a8a',
        'accent-green': '#22c55e',
        'accent-green-light': '#4ade80',
        'accent-green-dark': '#16a34a',
        'success-green': '#059669',
        'emerald-green': '#10b981',
        'emerald-green-light': '#34d399',
        'warm-gold': '#f59e0b',
        'warm-gold-light': '#fbbf24',
        'secondary-gray': '#374151',
        'muted-gray': '#6b7280',
        'gray-50': '#f9fafb',
        'gray-100': '#f3f4f6',
        'gray-200': '#e5e7eb',
        'gray-300': '#d1d5db',
        'gray-400': '#9ca3af',
        'gray-500': '#6b7280',
        'gray-600': '#4b5563',
        'gray-700': '#374151',
        'gray-800': '#1f2937',
        'gray-900': '#111827',
        'white': '#ffffff',
        'black': '#000000',
        'red-500': '#ef4444',
        'red-600': '#dc2626',
        'yellow-500': '#eab308',
        'yellow-600': '#ca8a04',
        'green-500': '#22c55e',
        'green-600': '#16a34a',
        'blue-500': '#3b82f6',
        'blue-600': '#2563eb',
        'purple-500': '#a855f7',
        'purple-600': '#9333ea'
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'display': ['Poppins', 'system-ui', 'sans-serif']
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem'
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem'
      },
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
        'glow': '0 0 20px rgba(34, 197, 94, 0.3)'
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'bounce-soft': 'bounceSoft 0.6s ease-in-out'
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' }
        },
        bounceSoft: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' }
        }
      }
    }
  },
  plugins: []
} 