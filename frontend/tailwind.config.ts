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
        ink: "#09111f",
        brass: "#d8a63f",
        moss: "#4f6f52",
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
        blink: {
          "0%, 80%, 100%": { opacity: "0.25" },
          "40%": { opacity: "1" },
        },
      },
      animation: {
        rise: "rise 480ms ease-out both",
        blink: "blink 1.2s infinite ease-in-out",
      },
    },
  },
  plugins: [],
}

export default config
