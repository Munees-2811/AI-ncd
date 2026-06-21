import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Signature accent — a refined "iris" (premium fintech/clinical), not teal.
        // Keeps the `brand-*` name so existing utilities restyle automatically.
        brand: {
          50: "#f1f0ff",
          100: "#e7e4ff",
          200: "#d0ccff",
          300: "#b2aaff",
          400: "#8d83fb",
          500: "#6c5cf0",
          600: "#5847e6",
          700: "#4736c4",
          800: "#392c9c",
          900: "#2c247a",
          950: "#1a1450",
        },
        // Warm-cool neutral ink scale for surfaces & text.
        ink: {
          50: "#f7f7f9",
          100: "#eeeef2",
          200: "#dcdce4",
          300: "#bcbcca",
          400: "#9494a6",
          500: "#727287",
          600: "#5a5a6e",
          700: "#494959",
          800: "#30303d",
          900: "#1a1a24",
          950: "#0c0c12",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        display: ["var(--font-display)", "var(--font-sans)", "sans-serif"],
      },
      letterSpacing: {
        tightest: "-0.03em",
      },
      borderRadius: {
        "2xl": "1.1rem",
        "3xl": "1.6rem",
      },
      boxShadow: {
        // Layered, soft — premium product feel.
        card: "0 1px 2px rgba(16,17,28,0.04), 0 12px 32px -16px rgba(16,17,28,0.18)",
        "card-lg": "0 1px 3px rgba(16,17,28,0.05), 0 24px 60px -28px rgba(16,17,28,0.30)",
        glow: "0 10px 40px -12px rgba(108,92,240,0.55)",
        "inner-line": "inset 0 1px 0 0 rgba(255,255,255,0.06)",
      },
      keyframes: {
        float: {
          "0%,100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
      },
      animation: {
        float: "float 6s ease-in-out infinite",
        "fade-up": "fade-up 0.6s cubic-bezier(0.22,1,0.36,1) both",
      },
    },
  },
  plugins: [],
};
export default config;
