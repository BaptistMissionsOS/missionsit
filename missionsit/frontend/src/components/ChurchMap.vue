<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
// OpenStreetMap through Leaflet. Pins are drawn as circles rather than image markers, so there
// are no marker images to serve, and each shows only the church's name.
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  churches: { type: Array, default: () => [] },
  height: { type: String, default: '28rem' },
  interactive: { type: Boolean, default: true },
})

const el = ref(null)
let map = null
let layer = null

function draw() {
  if (!map) return
  layer?.remove()
  layer = L.featureGroup(
    props.churches.map((c) =>
      L.circleMarker([c.lat, c.lng], {
        radius: 6,
        weight: 2,
        color: '#FFFFFF',
        fillColor: '#2D4E9C',
        fillOpacity: 1,
      }).bindTooltip(c.name, { direction: 'top', offset: [0, -6] }),
    ),
  ).addTo(map)
  if (props.churches.length) map.fitBounds(layer.getBounds(), { padding: [32, 32], maxZoom: 9 })
}

onMounted(() => {
  map = L.map(el.value, {
    center: [20, 10],
    zoom: 2,
    worldCopyJump: true,
    scrollWheelZoom: false,
    dragging: props.interactive,
    zoomControl: props.interactive,
    attributionControl: true,
  })
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map)
  draw()
})
watch(() => props.churches, draw)
onBeforeUnmount(() => map?.remove())
</script>

<template>
  <div
    ref="el"
    class="isolate z-0 w-full overflow-hidden rounded-7 border border-ink/10 bg-mist"
    :style="{ height }"
    role="region"
    :aria-label="`Map of ${churches.length} churches`"
  />
</template>
