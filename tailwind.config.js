const withOpacity = (variable) => `rgb(var(${variable}) / <alpha-value>)`;

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: withOpacity('--color-background'),
        },
        surface: {
          DEFAULT: withOpacity('--color-surface'),
        },
        muted: {
          DEFAULT: withOpacity('--color-muted'),
        },
        accent: {
          DEFAULT: withOpacity('--color-accent'),
        },
        success: '#10B981',
        danger: '#EF4444',
        border: {
          DEFAULT: withOpacity('--color-border'),
        },
        text: {
          primary: {
            DEFAULT: withOpacity('--color-text-primary'),
          },
          secondary: {
            DEFAULT: withOpacity('--color-text-secondary'),
          },
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.45s cubic-bezier(0.22,1,0.36,1)',
        'slide-up': 'slideUp 0.45s cubic-bezier(0.22,1,0.36,1)',
        'scale-in': 'scaleIn 0.2s cubic-bezier(0.22,1,0.36,1)',
        'shimmer': 'shimmer 2s infinite linear',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.98)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
      },
      boxShadow: {
        'card': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'card-hover': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
      },
    },
  },
  plugins: [],
}
