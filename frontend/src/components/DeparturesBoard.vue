<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
// The signature of the site: upcoming trips set like an airport departures board. Each
// destination flips into place once, on load, the way a split-flap board settles.
import { computed } from 'vue'
import { day } from '@/utils'

const props = defineProps({
  trips: { type: Array, default: () => [] },
  tiles: { type: Number, default: 12 },
})

const STATUS = {
  Open: { label: 'Open', class: 'text-[#8FD3AE]' },
  Planning: { label: 'Planning', class: 'text-white/60' },
  Full: { label: 'Full', class: 'text-[#F2C46D]' },
}

const rows = computed(() =>
  props.trips.map((trip, row) => {
    const place = (trip.destination || trip.name || '').toUpperCase()
    const letters = place.slice(0, props.tiles).padEnd(props.tiles, ' ').split('')
    return { ...trip, row, letters, overflow: place.length > props.tiles, place }
  }),
)
</script>

<template>
  <section class="rounded-7 bg-ink p-4 text-white shadow-[0_24px_60px_-30px_rgba(20,33,61,0.7)] sm:p-6" aria-labelledby="board-title">
    <div class="mb-4 flex items-center justify-between gap-4">
      <h2 id="board-title" class="font-display t-lead font-semibold">Departures</h2>
      <span class="lucide-plane-takeoff size-5 text-white/50" aria-hidden="true" />
    </div>

    <ol v-if="rows.length" class="divide-y divide-white/10">
      <li v-for="trip in rows" :key="trip.name">
        <RouterLink
          :to="{ path: '/trips', hash: `#${encodeURIComponent(trip.name)}` }"
          class="grid grid-cols-[3.25rem_minmax(0,1fr)_4.25rem] items-center gap-3 py-3 sm:grid-cols-[4.5rem_minmax(0,1fr)_5rem]"
          :aria-label="`${trip.name}, ${trip.place}, ${day(trip.start_date)}, ${trip.status}`"
        >
          <span class="text-sm font-semibold tabular-nums text-white/80">
            {{ day(trip.start_date, { month: 'short', day: 'numeric' }) }}
          </span>
          <span class="min-w-0">
            <!-- Tiles share the width they are given, so a narrow board shrinks them instead of
                 pushing into the status column. -->
            <span class="flex gap-[3px]" aria-hidden="true">
              <span
                v-for="(letter, i) in trip.letters"
                :key="i"
                class="flap grid aspect-[3/4] min-w-0 max-w-[1.4rem] flex-1 place-items-center rounded-[3px] bg-[#0B1427] text-[clamp(10px,2.6vw,14px)] font-semibold tabular-nums text-[#F4F1E4]"
                :style="{ animationDelay: `${trip.row * 90 + i * 35}ms` }"
              >{{ letter.trim() }}</span>
            </span>
            <span class="mt-1 block truncate text-xs text-white/55">
              {{ trip.name }}<template v-if="trip.missionary_name">, with {{ trip.missionary_name }}</template>
            </span>
          </span>
          <span class="text-right text-sm font-semibold" :class="STATUS[trip.status]?.class">
            {{ STATUS[trip.status]?.label || trip.status }}
          </span>
        </RouterLink>
      </li>
    </ol>
    <p v-else class="py-6 text-sm text-white/70">No trips are scheduled yet. New departures appear here as soon as they are planned.</p>
  </section>
</template>

<style scoped>
.flap {
  animation: flap 520ms cubic-bezier(0.3, 0.7, 0.2, 1) both;
  transform-origin: center;
  backface-visibility: hidden;
}

@keyframes flap {
  0% {
    transform: rotateX(90deg);
    opacity: 0;
  }
  60% {
    transform: rotateX(-12deg);
    opacity: 1;
  }
  100% {
    transform: none;
  }
}
</style>
