<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
import { computed, ref } from 'vue'
import MissionaryList from '@/components/MissionaryList.vue'
import PageState from '@/components/PageState.vue'
import { pageResource } from '@/data'

const list = pageResource('get_missionaries')
const country = ref('')
const countries = computed(() =>
  [...new Set((list.data || []).map((m) => m.field_country).filter(Boolean))].sort(),
)
const shown = computed(() =>
  (list.data || []).filter((m) => !country.value || m.field_country === country.value),
)
</script>

<template>
  <div class="page pt-12">
    <h1 class="heading t-h1">Our missionaries</h1>
    <p class="mt-3 max-w-2xl t-lead text-ink-soft">Read where each one serves and what they are working on, then pray for them or give to their support.</p>

    <PageState :resource="list" v-slot="{ data }">
      <div v-if="countries.length > 1" class="mt-8 flex flex-wrap gap-2" role="group" aria-label="Filter by country">
        <button
          v-for="c in ['', ...countries]"
          :key="c || 'all'"
          type="button"
          class="rounded-full border px-3.5 py-1.5 text-sm font-medium"
          :class="country === c ? 'border-airmail bg-airmail text-white' : 'border-ink/15 hover:border-airmail'"
          :aria-pressed="country === c"
          @click="country = c"
        >
          {{ c || 'Everywhere' }}
        </button>
      </div>
      <MissionaryList v-if="shown.length" class="mt-8" :missionaries="shown" />
      <p v-else class="mt-10 text-ink-soft">
        No missionary profiles are published yet. They appear here once a profile page is published in the desk.
      </p>
    </PageState>
  </div>
</template>
