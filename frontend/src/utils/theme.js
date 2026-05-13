// Central palette — import from here, never scatter raw hex values in components.
export const THEME = {
  bg: {
    page: '#0f1117',
    card: '#16181f',
    tooltip: '#1e2030',
    graphCanvas: '#0a0c12',
  },
  border: {
    default: '#2a2d3e',
    subtle: '#1a1c24',
  },
  text: {
    primary: '#e8e6e1',   // warm off-white
    secondary: '#9b9894', // warm muted
    muted: '#6b6765',     // warm dim
  },
  accent: {
    violet: '#7c3aed',
    violetLight: '#a78bfa',
    gold: '#f59e0b',
    goldLight: '#fbbf24',
    emerald: '#10b981',
    emeraldLight: '#34d399',
  },
  // Shared Recharts props — pass as explicit component props (Recharts ignores CSS vars)
  chart: {
    grid: '#262626',
    tick: '#737373',
    label: '#525252',
    link: '#404040',
  },
}

export const BOOK_TITLES = {
  1: "Philosopher's Stone",
  2: 'Chamber of Secrets',
  3: 'Prisoner of Azkaban',
  4: 'Goblet of Fire',
  5: 'Order of the Phoenix',
  6: 'Half-Blood Prince',
  7: 'Deathly Hallows',
}
