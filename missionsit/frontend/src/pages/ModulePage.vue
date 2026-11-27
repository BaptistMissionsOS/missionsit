<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
// One desk module in the portal: a tab for each of its DocTypes the member can read, and a
// list of their records, newest first.
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import { portalModules } from '@/data'
import { day } from '@/utils'

const props = defineProps({ module: { type: String, required: true } })
const route = useRoute()
const router = useRouter()

const mod = computed(() => (portalModules.data || []).find((m) => m.slug === props.module))
const doctype = computed(() => {
  const types = mod.value?.doctypes || []
  return types.find((d) => d.doctype === route.query.type)?.doctype || types[0]?.doctype
})

const search = ref('')
const rows = ref([])
const records = createResource({ url: '/api/method/missionsit.api.portal.get_records' })

async function load(more = false) {
  if (!doctype.value) return
  const data = await records.submit({
    doctype: doctype.value,
    search: search.value || undefined,
    start: more ? rows.value.length : 0,
  })
  rows.value = more ? [...rows.value, ...data.rows] : data.rows
}

let timer
watch(search, () => {
  clearTimeout(timer)
  timer = setTimeout(() => load(), 300)
})
watch(doctype, () => {
  search.value = ''
  rows.value = []
  load()
}, { immediate: true })

function pick(dt) {
  router.replace({ query: { type: dt } })
}
const titleOf = (row) => row[records.data?.title_field] || row.name
</script>

<template>
  <div>
    <p v-if="portalModules.loading && !portalModules.data" class="py-16 text-ink-soft">Loading…</p>
    <div v-else-if="!mod" class="py-10">
      <h1 class="heading t-h2">This part of the portal is not open to you</h1>
      <p class="mt-2 text-ink-soft">Your account does not have access to it. Ask the office if you think it should.</p>
    </div>
    <template v-else>
      <h1 class="heading t-h1">{{ mod.title }}</h1>

      <div v-if="mod.doctypes.length > 1" class="mt-5 flex flex-wrap gap-2" role="tablist" :aria-label="`${mod.title} lists`">
        <button
          v-for="d in mod.doctypes"
          :key="d.doctype"
          type="button"
          role="tab"
          :aria-selected="d.doctype === doctype"
          class="rounded-full border px-3.5 py-1.5 text-sm font-medium"
          :class="d.doctype === doctype ? 'border-airmail bg-airmail text-white' : 'border-ink/15 hover:border-airmail'"
          @click="pick(d.doctype)"
        >
          {{ d.label }}
        </button>
      </div>

      <label class="mt-6 flex max-w-sm items-center gap-2 rounded-4 border border-ink/15 px-3 py-2 focus-within:border-airmail">
        <span class="lucide-search size-4 text-ink-soft" aria-hidden="true" />
        <span class="sr-only">Search</span>
        <input v-model="search" type="search" placeholder="Search by name" class="w-full border-0 bg-transparent p-0 text-[15px] focus:outline-none focus:ring-0" />
      </label>

      <p v-if="records.error" class="mt-6 text-[#C33A3A]">{{ records.error.messages?.[0] || records.error.message }}</p>
      <div v-else class="mt-4 overflow-x-auto">
        <table class="w-full min-w-[32rem] text-left text-sm">
          <thead class="border-b border-ink/10 text-ink-soft">
            <tr>
              <th class="py-2 pr-4 font-medium">Name</th>
              <th v-for="c in records.data?.columns || []" :key="c.fieldname" class="py-2 pr-4 font-medium">{{ c.label }}</th>
              <th class="py-2 text-right font-medium">Updated</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in rows"
              :key="row.name"
              class="cursor-pointer border-b border-ink/10 hover:bg-mist"
              @click="router.push(`/portal/${module}/${encodeURIComponent(doctype)}/${encodeURIComponent(row.name)}`)"
            >
              <td class="py-3 pr-4">
                <RouterLink :to="`/portal/${module}/${encodeURIComponent(doctype)}/${encodeURIComponent(row.name)}`" class="font-semibold text-ink hover:text-airmail" @click.stop>
                  {{ titleOf(row) }}
                </RouterLink>
              </td>
              <td v-for="c in records.data?.columns || []" :key="c.fieldname" class="py-3 pr-4 text-ink-soft">
                {{ c.fieldtype === 'Date' ? day(row[c.fieldname]) : row[c.fieldname] ?? '' }}
              </td>
              <td class="py-3 text-right tabular-nums text-ink-soft">{{ day(row.modified) }}</td>
            </tr>
          </tbody>
        </table>
        <p v-if="!records.loading && !rows.length" class="py-8 text-ink-soft">
          {{ search ? 'Nothing matches that name.' : 'Nothing here yet.' }}
        </p>
        <button
          v-if="records.data?.more"
          type="button"
          class="mt-4 rounded-full border border-ink/15 px-4 py-2 text-sm font-medium hover:border-airmail"
          :disabled="records.loading"
          @click="load(true)"
        >
          {{ records.loading ? 'Loading…' : 'Show more' }}
        </button>
      </div>
    </template>
  </div>
</template>
