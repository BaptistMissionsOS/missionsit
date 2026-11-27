<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
import { computed, watch } from 'vue'
import { Avatar } from 'frappe-ui'
import GoalBar from '@/components/GoalBar.vue'
import PageState from '@/components/PageState.vue'
import { pageResource } from '@/data'
import { day, links } from '@/utils'

const props = defineProps({ slug: { type: String, required: true } })
const res = pageResource('get_missionary', { slug: props.slug })
// Moving from one profile to another reuses this page, so fetch the new one.
watch(
  () => props.slug,
  (slug) => res.submit({ slug }),
)
const profile = computed(() => res.data?.profile)
</script>

<template>
  <div class="page pt-10">
    <RouterLink to="/missionaries" class="inline-flex items-center gap-1 text-sm font-medium text-ink-soft hover:text-airmail">
      <span class="lucide-chevron-left size-4" aria-hidden="true" />All missionaries
    </RouterLink>

    <PageState :resource="res" v-slot="{ data }">
      <div class="mt-6 grid gap-12 lg:grid-cols-[minmax(0,1fr)_20rem]">
        <article>
          <div class="flex flex-wrap items-center gap-5">
            <img v-if="profile.image" :src="profile.image" alt="" class="size-24 rounded-full object-cover" />
            <Avatar v-else :label="profile.display_name" size="3xl" />
            <div>
              <h1 class="heading t-h1">{{ profile.display_name }}</h1>
              <p v-if="profile.headline" class="mt-1 t-lead text-ink-soft">{{ profile.headline }}</p>
              <p class="mt-2 flex flex-wrap gap-x-4 text-sm">
                <span v-if="profile.field_country" class="inline-flex items-center gap-1 font-medium text-airmail">
                  <span class="lucide-map-pin size-4" aria-hidden="true" />{{ profile.field_country }}
                </span>
                <span v-if="profile.status" class="text-ink-soft">{{ profile.status }}</span>
              </p>
            </div>
          </div>
          <p v-if="profile.summary" class="mt-8 max-w-[65ch] t-lead leading-8 text-ink">{{ profile.summary }}</p>
          <div v-if="profile.bio" class="prose-ink mt-6" v-html="profile.bio" />
        </article>

        <aside class="grid content-start gap-6">
          <section v-for="p in data.pages" :key="p.name" class="rounded-6 border border-ink/10 p-5">
            <h2 class="heading t-h4">{{ p.title }}</h2>
            <GoalBar class="mt-4" :raised="p.raised" :goal="p.goal_amount" :currency="p.currency" />
            <a :href="links.give(p.slug)" class="mt-5 flex justify-center rounded-full bg-harvest px-4 py-2.5 text-sm font-semibold text-white hover:bg-harvest-dark">
              Give to {{ profile.display_name.split(' ')[0] }}
            </a>
            <p v-if="p.allow_recurring" class="mt-2 text-center text-xs text-ink-soft">Monthly giving is available.</p>
          </section>
          <section v-if="data.trips.length" class="rounded-6 bg-mist p-5">
            <h2 class="heading t-h4">Go with {{ profile.display_name.split(' ')[0] }}</h2>
            <ul class="mt-3 grid gap-3">
              <li v-for="t in data.trips" :key="t.name">
                <RouterLink :to="{ path: '/portal/trips', hash: `#${encodeURIComponent(t.name)}` }" class="block hover:text-airmail">
                  <span class="font-semibold">{{ t.name }}</span>
                  <span class="block text-sm text-ink-soft">{{ t.destination }}, {{ day(t.start_date) }}</span>
                </RouterLink>
              </li>
            </ul>
          </section>
        </aside>
      </div>
    </PageState>
  </div>
</template>
