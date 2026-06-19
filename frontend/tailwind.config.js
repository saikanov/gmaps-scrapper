/** Baraquette internal-tools palette (see DESIGN.md).
 *  Identity: dark shell + light workspace + a single, scarce gold accent. */
export default {
  content: ["./index.html", "./src/**/*.{vue,ts}"],
  theme: {
    extend: {
      colors: {
        // === Brand / accent — gold is scarce: one primary thing per screen ===
        gold: {
          DEFAULT: "#DBB600", // primary action, active state, key metric
          deep: "#B89800", // hover / gold text on light (contrast-safe-ish)
          50: "rgba(219,182,0,0.12)", // tint for pills, badges, active rows
        },

        // === Text neutrals (workspace) ===
        ink: {
          DEFAULT: "#1A1A1A", // primary text
          700: "#1A1A1A", // strong text / headings
          500: "#595959", // secondary text
          300: "#969696", // muted labels, captions
        },

        // === Dark shell (sidebar, top bar, app chrome) ===
        shell: {
          DEFAULT: "#0D0D0D", // deepest: sidebar, nav
          mid: "#1A1A1A", // secondary dark surface
          card: "#232323", // card/panel on dark
          panel: "#292B2B", // raised panel on dark
        },

        // === Light surfaces ===
        paper: "#F2F2F2", // page background
        border: "#D9D9D9", // hairline dividers, card borders

        // === Warm accent kept distinct from gold (won / tier-1) ===
        amber: {
          DEFAULT: "#C77D00",
          400: "#C77D00",
          200: "#E8C089",
          50: "rgba(199,125,0,0.12)",
        },

        // === Semantic status (DESIGN.md §2.5) — never gold ===
        success: "#2E7D5B",
        warning: "#C77D00",
        danger: "#C0392B",
        info: "#2D6CB5",
        status: {
          new: "#6B7280",
          contacted: "#2D6CB5",
          replied: "#4F46E5",
          qualified: "#2E7D5B",
          rejected: "#C0392B",
          won: "#C77D00",
        },
      },
      // Single typeface across the app (DESIGN.md §3). Aliases share the family
      // so existing font-display / font-mono usages stay consistent.
      fontFamily: {
        display: ['"Plus Jakarta Sans"', "system-ui", "sans-serif"],
        sans: ['"Plus Jakarta Sans"', "system-ui", "sans-serif"],
        mono: ['"Plus Jakarta Sans"', "system-ui", "sans-serif"],
      },
      boxShadow: {
        // Shadows only for floating elements (DESIGN.md §4.3).
        card: "0 4px 24px rgba(0,0,0,0.08)",
        rail: "1px 0 0 rgba(0,0,0,0.08)",
        sm: "0 4px 24px rgba(0,0,0,0.08)",
        md: "0 16px 40px rgba(0,0,0,0.12)",
        lg: "0 18px 40px rgba(0,0,0,0.45)",
      },
      borderRadius: {
        sm: "6px", // buttons, inputs, badges — default
        card: "12px", // cards, panels, modals
        lg: "24px",
      },
      transitionTimingFunction: {
        panel: "cubic-bezier(0.22,1,0.36,1)",
      },
    },
  },
  plugins: [],
};
