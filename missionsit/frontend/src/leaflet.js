// This source code is freely given for the sake of the gospel (Matthew 10:8)
// and is licensed under MIT No Attribution (MIT-0).

// Leaflet.markercluster attaches itself to a global `L`, so expose Leaflet before loading it.
// Kept in its own module because ES imports run in order: this one finishes first.
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

window.L = L

export default L
