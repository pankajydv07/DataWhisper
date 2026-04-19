import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "rgb(var(--ink-rgb) / <alpha-value>)",
        "ink-soft": "rgb(var(--ink-soft-rgb) / <alpha-value>)",
        paper: "rgb(var(--paper-rgb) / <alpha-value>)",
        "paper-muted": "rgb(var(--paper-muted-rgb) / <alpha-value>)",
        brass: "rgb(var(--brass-rgb) / <alpha-value>)",
        "brass-soft": "rgb(var(--brass-soft-rgb) / <alpha-value>)",
        moss: "rgb(var(--moss-rgb) / <alpha-value>)",
        line: "var(--line)",
        danger: "rgb(var(--danger-rgb) / <alpha-value>)",
        warning: "rgb(var(--warning-rgb) / <alpha-value>)",
      },
      fontFamily: {
        display: ["Newsreader", "Georgia", "serif"],
        sans: ["Space Grotesk", "Aptos", "Segoe UI", "sans-serif"],
      },
      keyframes: {
        rise: {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        reveal: {
          "0%": { opacity: "0", transform: "translateY(24px) scale(0.98)" },
          "100%": { opacity: "1", transform: "translateY(0) scale(1)" },
        },
        drift: {
          "0%": { transform: "translate3d(0, 0, 0)" },
          "50%": { transform: "translate3d(18px, -12px, 0)" },
          "100%": { transform: "translate3d(0, 0, 0)" },
        },
        pulseSoft: {
          "0%, 100%": { opacity: "0.42" },
          "50%": { opacity: "1" },
        },
        blink: {
          "0%, 80%, 100%": { opacity: "0.25" },
          "40%": { opacity: "1" },
        },
      },
      animation: {
        rise: "rise 480ms ease-out both",
        reveal: "reveal 720ms cubic-bezier(.2,.8,.2,1) both",
        drift: "drift 10s ease-in-out infinite",
        "pulse-soft": "pulseSoft 1.8s ease-in-out infinite",
        blink: "blink 1.2s infinite ease-in-out",
      },
    },
  },
  plugins: [],
}

export default config
