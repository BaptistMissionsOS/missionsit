<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
// OpenStreetMap through Leaflet, with nearby churches gathered into clusters until you zoom in.
// Each pin shows only the church's name.
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from '@/leaflet'
import 'leaflet.markercluster'
import 'leaflet.markercluster/dist/MarkerCluster.css'

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
    maxBounds: WORLD.pad(0.05),
    maxBoundsViscosity: 1,
    scrollWheelZoom: false,
    dragging: props.interactive,
    zoomControl: props.interactive,
    doubleClickZoom: props.interactive,
    attributionControl: true,
  })
  // OpenStreetMap's own tiles need no API key. The church-map__tiles class quiets them to soft
  // greys (see the style below), so the blue churches stand out.
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    noWrap: true,
    bounds: WORLD,
    className: 'church-map__tiles',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map)
  fitWorldWidth()
  draw()
  resize = new ResizeObserver(() => {
    map.invalidateSize()
    fitWorldWidth()
  })
  resize.observe(el.value)
})
watch(() => props.churches, draw)
onBeforeUnmount(() => {
  resize?.disconnect()
  map?.remove()
})
</script>

<template>
  <div
    ref="el"
    class="isolate z-0 w-full overflow-hidden rounded-7 border border-ink/10 bg-[#D4DADC]"
    :style="{ height }"
    role="region"
    :aria-label="`Map of ${churches.length.toLocaleString()} churches`"
  />
</template>

<style>
/* OpenStreetMap's colours, quieted: grey land and sea, labels still legible. */
.church-map__tiles {
  filter: grayscale(1) brightness(1.06) contrast(0.88);
}

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
