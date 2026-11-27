<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
// One record, read-only, in the sections the desk form uses. Only the fields the member may
// read come back from the server.
import { computed } from 'vue'
import { createResource } from 'frappe-ui'
import PageState from '@/components/PageState.vue'
import { portalModules } from '@/data'
import { day } from '@/utils'

const props = defineProps({
  module: { type: String, required: true },
  doctype: { type: String, required: true },
  name: { type: String, required: true },
})

const record = createResource({
  url: '/api/method/missionsit.api.portal.get_record',
  params: { doctype: props.doctype, name: props.name },
  auto: true,
})
const mod = computed(() => (portalModules.data || []).find((m) => m.slug === props.module))
const RICH = ['Text Editor', 'HTML Editor']
</script>

<template>
  <div>
    <RouterLink :to="{ path: `/portal/${module}`, query: { type: doctype } }" class="inline-flex items-center gap-1 text-sm font-medium text-ink-soft hover:text-airmail">
      <span class="lucide-chevron-left size-4" aria-hidden="true" />{{ mod?.title || 'Back' }}
    </RouterLink>

    <PageState :resource="record" v-slot="{ data }">
      <div class="mt-4 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 class="heading t-h1">{{ data.title }}</h1>
          <p class="mt-1 text-sm text-ink-soft">{{ data.name }}, updated {{ day(data.modified) }}</p>
        </div>
        <a v-if="data.desk_url" :href="data.desk_url" class="inline-flex items-center gap-1.5 rounded-full border border-ink/15 px-4 py-2 text-sm font-medium hover:border-airmail hover:text-airmail">
          Open in desk<span class="lucide-external-link size-4" aria-hidden="true" />
        </a>
      </div>

      <section v-for="(section, i) in data.sections" :key="i" class="mt-8">
        <h2 v-if="section.label" class="heading t-h4 mb-3">{{ section.label }}</h2>
        <dl class="grid gap-x-8 gap-y-4 border-t border-ink/10 pt-4 sm:grid-cols-2">
          <div
            v-for="f in section.fields"
            :key="f.fieldname"
            :class="{ 'sm:col-span-2': f.columns || RICH.includes(f.fieldtype) || ['Text', 'Small Text', 'Long Text'].includes(f.fieldtype) }"
          >
            <dt class="text-sm text-ink-soft">{{ f.label }}</dt>
            <dd class="mt-1 text-[15px] text-ink">
              <div v-if="RICH.includes(f.fieldtype)" class="prose-ink" v-html="f.value" />
              <img v-else-if="f.fieldtype === 'Attach Image'" :src="f.value" alt="" class="mt-1 max-h-48 rounded-6" />
              <a v-else-if="f.fieldtype === 'Attach'" :href="f.value" class="font-medium text-airmail hover:underline">Open the file</a>
              <table v-else-if="f.columns" class="mt-1 w-full text-left text-sm">
                <thead class="text-ink-soft">
                  <tr><th v-for="c in f.columns" :key="c.fieldname" class="py-1.5 pr-4 font-medium">{{ c.label }}</th></tr>
                </thead>
                <tbody>
                  <tr v-for="(row, r) in f.rows" :key="r" class="border-t border-ink/10">
                    <td v-for="c in f.columns" :key="c.fieldname" class="py-2 pr-4">{{ row[c.fieldname] }}</td>
                  </tr>
                </tbody>
              </table>
              <span v-else class="whitespace-pre-line">{{ f.value }}</span>
            </dd>
          </div>
        </dl>
      </section>
    </PageState>
  </div>
</template>
