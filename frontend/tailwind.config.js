/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: {
          base: "#020617",
          sidebar: "#0F172A",
          panel: "#111827",
          raised: "#1E293B",
          line: "#334155",
        },
        content: {
          primary: "#F8FAFC",
          secondary: "#CBD5E1",
          muted: "#94A3B8",
        },
        accent: {
          DEFAULT: "#38BDF8",
          strong: "#0EA5E9",
          soft: "#082F49",
        },
        success: "#2DD4BF",
        danger: "#FB7185",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      boxShadow: {
        panel: "0 18px 48px rgba(2, 6, 23, 0.34)",
      },
      borderRadius: {
        panel: "18px",
      },
    },
  },
  plugins: [],
};
