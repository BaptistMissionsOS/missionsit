// This source code is freely given for the sake of the gospel (Matthew 10:8)
// and is licensed under MIT No Attribution (MIT-0).

export function money(value, currency) {
  const amount = Number(value || 0)
  try {
    return new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency: currency || 'USD',
      maximumFractionDigits: 0,
    }).format(amount)
  } catch {
    return amount.toLocaleString()
  }
}

export function day(iso, options = { day: 'numeric', month: 'short', year: 'numeric' }) {
  if (!iso) return ''
  return new Date(`${String(iso).slice(0, 10)}T00:00:00`).toLocaleDateString(undefined, options)
}

export function percent(part, whole) {
  if (!whole) return 0
  return Math.max(0, Math.min(100, Math.round((Number(part || 0) / Number(whole)) * 100)))
}

// Where the existing server-rendered pages live; the web app links out to them.
export const links = {
  give: (slug) => `/donate/${encodeURIComponent(slug)}`,
  apply: (trip) => `/apply/${encodeURIComponent(trip)}`,
  signIn: (to = '/missions/portal') => `/login?redirect-to=${encodeURIComponent(to)}`,
  account: '/me',
  desk: '/desk',
}
