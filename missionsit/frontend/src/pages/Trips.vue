<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
import { nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import DeparturesBoard from '@/components/DeparturesBoard.vue'
import PageState from '@/components/PageState.vue'
import { pageResource, site } from '@/data'
import { day, links } from '@/utils'

const trips = pageResource('get_trips')
const route = useRoute()

// Arriving from the board with #<trip>, bring that trip into view once it has loaded.
watch(
  () => [trips.data, route.hash],
  async () => {
    if (!trips.data || !route.hash) return
    await nextTick()
    document.getElementById(decodeURIComponent(route.hash.slice(1)))?.scrollIntoView({ block: 'start' })
  },
  { immediate: true },
)
</script>

<template>
  <div>
    <div class="grid items-start gap-10 lg:grid-cols-[minmax(0,1fr)_minmax(0,28rem)]">
      <div>
        <h1 class="heading t-h1">Short-term trips</h1>
        <p class="mt-3 max-w-xl t-lead text-ink-soft">
          Serve alongside our missionaries for a week or two. Each trip is led by someone on the field, and the team raises its support together.
        </p>
        <p v-if="site.data && !site.data.enable_trip_applications" class="mt-4 rounded-4 bg-mist px-4 py-3 text-sm text-ink-soft">
          Applications are closed for now. Check back soon, or ask the trip leader directly.
        </p>
      </div>
      <DeparturesBoard :trips="trips.data || []" :tiles="12" />
    </div>

    <PageState :resource="trips" v-slot="{ data }">
      <ul class="mt-14 grid gap-6">
        <li
          v-for="t in data"
          :id="t.name"
          :key="t.name"
          class="scroll-mt-24 grid gap-6 rounded-6 border border-ink/10 p-6 md:grid-cols-[12rem_minmax(0,1fr)_auto]"
        >
          <div>
            <p class="heading t-h4">{{ day(t.start_date, { day: 'numeric', month: 'long' }) }}</p>
            <p class="text-sm text-ink-soft">to {{ day(t.end_date) }}</p>
          </div>
          <div class="min-w-0">
            <h2 class="heading t-h2">{{ t.name }}</h2>
            <p class="mt-1 text-ink-soft">
              {{ t.destination }}<template v-if="t.missionary_name">, led with {{ t.missionary_name }}</template>
            </p>
            <div v-if="t.description" class="prose-ink mt-4" v-html="t.description" />
          </div>
          <div class="md:text-right">
            <a
              v-if="t.can_apply"
              :href="links.apply(t.name)"
              class="inline-flex rounded-full bg-airmail px-5 py-2.5 text-sm font-semibold text-white hover:bg-airmail-dark"
            >
              Apply for this trip
            </a>
            <p v-else class="text-sm font-medium text-ink-soft">
              {{ t.status === 'Full' ? 'This team is full' : t.status === 'Planning' ? 'Applications open soon' : 'Applications are closed' }}
            </p>
          </div>
        </li>
      </ul>
      <p v-if="!data.length" class="mt-10 text-ink-soft">No trips are scheduled yet.</p>
    </PageState>
  </div>
</template>
