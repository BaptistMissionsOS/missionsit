<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
import { computed } from 'vue'
import DeparturesBoard from '@/components/DeparturesBoard.vue'
import MissionaryList from '@/components/MissionaryList.vue'
import GoalBar from '@/components/GoalBar.vue'
import PageState from '@/components/PageState.vue'
import ChurchMap from '@/components/ChurchMap.vue'
import { site, pageResource, directory, loadDirectory } from '@/data'
import { links } from '@/utils'

const home = pageResource('get_home')
loadDirectory()
const churches = computed(() => directory.data?.churches || [])

// One plain sentence about the work, rather than a row of big numbers.
const reach = computed(() => {
  const c = site.data?.counts
  if (!c?.missionaries) return ''
  const people = c.missionaries === 1 ? '1 missionary' : `${c.missionaries} missionaries`
  const places = c.countries === 1 ? '1 country' : `${c.countries} countries`
  return `${people} serving in ${places}.`
})
</script>

<template>
  <section class="border-b border-ink/10 bg-gradient-to-b from-mist to-white">
    <div class="page grid items-center gap-10 py-14 lg:grid-cols-[1.05fr_1fr] lg:py-20">
      <div>
        <h1 class="heading t-hero">Go ye into all the world.</h1>
        <p class="mt-5 max-w-[34rem] t-lead leading-8 text-ink-soft">
          {{ site.data?.welcome || 'We send missionaries to the field and stand behind them in prayer and giving. Meet them, join a short-term trip, or give to the work.' }}
        </p>
        <p v-if="reach" class="mt-3 text-base font-medium text-airmail">{{ reach }}</p>
        <div class="mt-8 flex flex-wrap gap-3">
          <RouterLink to="/missionaries" class="rounded-full bg-airmail px-5 py-3 text-sm font-semibold text-white hover:bg-airmail-dark">
            Meet our missionaries
          </RouterLink>
          <RouterLink to="/give" class="rounded-full bg-harvest px-5 py-3 text-sm font-semibold text-white hover:bg-harvest-dark">
            Give to the work
          </RouterLink>
        </div>
      </div>
      <DeparturesBoard :trips="home.data?.departures || []" />
    </div>
  </section>

  <PageState :resource="home" v-slot="{ data }">
    <section v-if="data.missionaries.length" class="page pt-16" aria-labelledby="sent">
      <div class="mb-6 flex items-end justify-between gap-4">
        <div>
          <h2 id="sent" class="heading t-h2">The people we send</h2>
          <p class="mt-2 text-ink-soft">Each one is on the field, at home on assignment, or raising support to go.</p>
        </div>
        <RouterLink to="/missionaries" class="shrink-0 text-sm font-semibold text-airmail hover:underline">See everyone</RouterLink>
      </div>
      <MissionaryList :missionaries="data.missionaries" />
    </section>

    <section class="page pt-16" aria-labelledby="directory-home">
      <div class="grid items-center gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]">
        <div>
          <h2 id="directory-home" class="heading t-h2">Church Directory</h2>
          <p class="t-lead mt-3 text-ink-soft">
            Churches that welcome missionaries, on one map. Know one that is missing? Add it, or send a whole list, and our team checks each before it appears.
          </p>
          <p v-if="directory.data" class="mt-2 font-medium text-airmail">
            {{ churches.length === 1 ? '1 church on the map' : `${churches.length.toLocaleString()} churches on the map` }}
          </p>
          <div class="mt-6 flex flex-wrap gap-3">
            <RouterLink to="/directory" class="rounded-full bg-airmail px-5 py-3 text-sm font-semibold text-white hover:bg-airmail-dark">Open the directory</RouterLink>
            <RouterLink :to="{ path: '/directory', hash: '#submit-title' }" class="rounded-full border border-ink/15 px-5 py-3 text-sm font-semibold hover:border-airmail hover:text-airmail">Add a church</RouterLink>
          </div>
        </div>
        <RouterLink to="/directory" aria-label="Open the Church Directory map" class="block">
          <ChurchMap :churches="churches" height="20rem" :interactive="false" />
        </RouterLink>
      </div>
    </section>

    <section v-if="data.pages.length || data.campaigns.length" class="page pt-16" aria-labelledby="give-home">
      <div class="mb-6 flex items-end justify-between gap-4">
        <div>
          <h2 id="give-home" class="heading t-h2">Where your gift goes</h2>
          <p class="mt-2 text-ink-soft">Every gift goes to a named missionary or project, and you can see how close each one is.</p>
        </div>
        <RouterLink to="/give" class="shrink-0 text-sm font-semibold text-airmail hover:underline">All ways to give</RouterLink>
      </div>
      <div class="grid gap-6 md:grid-cols-3">
        <article v-for="c in data.campaigns" :key="c.name" class="rounded-6 border border-ink/10 p-5">
          <p class="text-sm text-ink-soft">{{ c.campaign_type || 'Campaign' }}</p>
          <h3 class="heading t-h3 mt-1">{{ c.campaign_name }}</h3>
          <p v-if="c.missionary_name" class="mt-1 text-sm text-ink-soft">For {{ c.missionary_name }}</p>
          <GoalBar class="mt-5" :raised="c.amount_raised" :goal="c.goal_amount" />
        </article>
        <article v-for="p in data.pages" :key="p.name" class="flex flex-col rounded-6 border border-ink/10 p-5">
          <h3 class="heading t-h3">{{ p.title }}</h3>
          <p v-if="p.missionary_name" class="mt-1 text-sm text-ink-soft">For {{ p.missionary_name }}</p>
          <GoalBar class="mt-5" :raised="p.raised" :goal="p.goal_amount" :currency="p.currency" />
          <a :href="links.give(p.slug)" class="mt-5 inline-flex self-start rounded-full bg-harvest px-4 py-2 text-sm font-semibold text-white hover:bg-harvest-dark">
            Give
          </a>
        </article>
      </div>
    </section>
  </PageState>
</template>
