<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
// OpenStreetMap through Leaflet, with nearby churches gathered into clusters until you zoom in.
// Each pin shows only the church's name.
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from '@/leaflet'
import 'leaflet.markercluster'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'maplibre-gl/dist/maplibre-gl.css'
import '@maplibre/maplibre-gl-leaflet'
import { site } from '@/data'

const props = defineProps({
  churches: { type: Array, default: () => [] },
  height: { type: String, default: '28rem' },
  interactive: { type: Boolean, default: true },
})

const el = ref(null)
let map = null
let clusters = null

// A small dot for one church, drawn in CSS so there are no marker images to serve.
const pin = L.divIcon({ className: 'church-pin', iconSize: [12, 12], iconAnchor: [6, 6] })

function clusterIcon(cluster) {
  const count = cluster.getChildCount()
  const size = count < 10 ? 30 : count < 100 ? 36 : count < 1000 ? 44 : 52
  const label = count >= 1000 ? `${(count / 1000).toFixed(count >= 10000 ? 0 : 1)}k` : String(count)
  return L.divIcon({
    html: `<span>${label}</span>`,
    className: 'church-cluster',
    iconSize: [size, size],
  })
}

function draw() {
  if (!map) return
  clusters?.remove()
  clusters = L.markerClusterGroup({
    chunkedLoading: true,
    showCoverageOnHover: false,
    spiderfyOnMaxZoom: true,
    maxClusterRadius: 50,
    iconCreateFunction: clusterIcon,
  })
  clusters.addLayers(
    props.churches.map((c) =>
      L.marker([c.lat, c.lng], { icon: pin, title: c.name, alt: c.name, keyboard: false }).bindTooltip(c.name, {
        direction: 'top',
        offset: [0, -6],
      }),
    ),
  )
  map.addLayer(clusters)
  // Churches across the world: show the whole world; otherwise frame where they are.
  const bounds = clusters.getBounds()
  if (!props.churches.length || !bounds.isValid()) return
  if (bounds.getEast() - bounds.getWest() > 180) map.setView([24, 10], map.getMinZoom())
  else map.fitBounds(bounds, { padding: [24, 24], maxZoom: 9 })
}

// The base map is a MapLibre GL vector style drawn under Leaflet, so it stays sharp at every
// zoom. The style URL comes from the site (OpenFreeMap's Positron unless the site config names
// its own tile server). If WebGL is unavailable, fall back to OpenStreetMap's raster tiles.
const ATTRIBUTION =
  '&copy; <a href="https://openfreemap.org">OpenFreeMap</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
let base = null
let baseStyle = null

function setBase(style) {
  if (!map || !style || style === baseStyle) return
  base?.remove()
  baseStyle = style
  try {
    base = L.maplibreGL({ style, attribution: ATTRIBUTION, interactive: false }).addTo(map)
  } catch {
    base = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      noWrap: true,
      bounds: WORLD,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map)
  }
}

// One world, edge to edge: the map cannot be dragged past it, and at its furthest zoom the
// world exactly fills the box's width, so there are no grey bands and no repeated copies.
const WORLD = L.latLngBounds([-60, -180], [84, 180])

function fitWorldWidth() {
  if (!map) return
  const width = el.value.clientWidth || 256
  // Rounded up to the next quarter step, so the world always covers the full width.
  const zoom = Math.max(0, Math.ceil(Math.log2(width / 256) * 4) / 4)
  map.setMinZoom(zoom)
  if (map.getZoom() < zoom) map.setZoom(zoom)
}

let resize = null

onMounted(() => {
  map = L.map(el.value, {
    center: [24, 10],
    zoom: 2,
    zoomSnap: 0.25,
    // The cluster plugin needs a top zoom; vector tiles stay sharp well past street level.
    maxZoom: 18,
    maxBounds: WORLD.pad(0.05),
    maxBoundsViscosity: 1,
    // The Directory map zooms with the mouse wheel; the Home preview does not, so scrolling the
    // page past it is never caught by the map.
    scrollWheelZoom: props.interactive,
    wheelPxPerZoomLevel: 90,
    dragging: props.interactive,
    zoomControl: props.interactive,
    doubleClickZoom: props.interactive,
    attributionControl: true,
  })
  setBase(site.data?.map_style)
  fitWorldWidth()
  draw()
  resize = new ResizeObserver(() => {
    map.invalidateSize()
    fitWorldWidth()
  })
  resize.observe(el.value)
})
watch(() => props.churches, draw)
// The site settings may arrive after the map is drawn.
watch(() => site.data?.map_style, setBase)
onBeforeUnmount(() => {
  resize?.disconnect()
  map?.remove()
})
</script>

<template>
  <div
    ref="el"
    class="isolate z-0 w-full overflow-hidden rounded-7 border border-ink/10 bg-[#F2F3F0]"
    :style="{ height }"
    role="region"
    :aria-label="`Map of ${churches.length.toLocaleString()} churches`"
  />
</template>

<style>
.church-pin {
  border: 2px solid #fff;
  border-radius: 50%;
  background: #2d4e9c;
  box-shadow: 0 1px 3px rgba(20, 33, 61, 0.35);
}

/* Clusters: airmail blue with a soft halo, the count in white. */
.church-cluster {
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: rgba(45, 78, 156, 0.25);
}

.church-cluster span {
  display: grid;
  place-items: center;
  width: calc(100% - 8px);
  height: calc(100% - 8px);
  border-radius: 50%;
  background: #2d4e9c;
  color: #fff;
  font: 600 12px/1 Inter, system-ui, sans-serif;
  font-variant-numeric: tabular-nums;
}
</style>
