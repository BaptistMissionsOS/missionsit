<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
import GoalBar from '@/components/GoalBar.vue'
import PageState from '@/components/PageState.vue'
import { pageResource, site } from '@/data'
import { day, links } from '@/utils'

const give = pageResource('get_give')
</script>

<template>
  <div class="page pt-12">
    <h1 class="heading t-h1">Give to the work</h1>
    <p class="mt-3 max-w-2xl t-lead text-ink-soft">
      Choose a missionary or a project. Gifts are processed securely, you get a receipt by email, and you can give once or every month.
    </p>
    <p v-if="site.data && !site.data.enable_donations" class="mt-4 rounded-4 bg-mist px-4 py-3 text-sm text-ink-soft">
      Online giving is paused for now. To give, contact the office.
    </p>

    <PageState :resource="give" v-slot="{ data }">
      <section v-if="data.pages.length" class="mt-10" aria-labelledby="pages">
        <h2 id="pages" class="heading t-h2">Missionaries and funds</h2>
        <ul class="mt-4 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <li v-for="p in data.pages" :key="p.name" class="flex flex-col rounded-6 border border-ink/10 p-5">
            <h3 class="heading t-h3">{{ p.title }}</h3>
            <p v-if="p.missionary_name" class="mt-1 text-sm text-ink-soft">For {{ p.missionary_name }}</p>
            <GoalBar class="mt-5" :raised="p.raised" :goal="p.goal_amount" :currency="p.currency" />
            <div class="mt-auto pt-5">
              <a
                v-if="site.data?.enable_donations !== false"
                :href="links.give(p.slug)"
                class="inline-flex rounded-full bg-harvest px-4 py-2 text-sm font-semibold text-white hover:bg-harvest-dark"
              >
                Give
              </a>
              <span v-if="p.allow_recurring" class="ml-3 text-xs text-ink-soft">Monthly giving available</span>
            </div>
          </li>
        </ul>
      </section>

      <section v-if="data.campaigns.length" class="mt-14" aria-labelledby="campaigns">
        <h2 id="campaigns" class="heading t-h2">Campaigns</h2>
        <ul class="mt-4 grid gap-6 md:grid-cols-2">
          <li v-for="c in data.campaigns" :key="c.name" class="rounded-6 bg-mist p-5">
            <p class="text-sm text-ink-soft">
              {{ c.campaign_type || 'Campaign' }}<template v-if="c.end_date">, ends {{ day(c.end_date) }}</template>
            </p>
            <h3 class="heading t-h3 mt-1">{{ c.campaign_name }}</h3>
            <p v-if="c.missionary_name" class="mt-1 text-sm text-ink-soft">For {{ c.missionary_name }}</p>
            <GoalBar class="mt-5" :raised="c.amount_raised" :goal="c.goal_amount" />
          </li>
        </ul>
      </section>

      <p v-if="!data.pages.length && !data.campaigns.length" class="mt-10 text-ink-soft">
        There is nowhere to give online yet. Gift pages appear here once one is made active in the desk.
      </p>
    </PageState>
  </div>
</template>
