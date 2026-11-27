<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
// Submit one church, or a list of them, to the directory's review queue. No sign-in needed:
// every church waits in Pending Review until someone on the team approves it.
import { computed, reactive, ref } from 'vue'
import { call } from 'frappe-ui'

const COLUMNS = [
  'church_name',
  'pastor_name',
  'address_line',
  'city',
  'state_province',
  'postal_code',
  'country',
  'phone',
  'email',
  'website',
]
const HEADINGS = {
  church_name: 'Church name',
  pastor_name: 'Pastor',
  address_line: 'Street address',
  city: 'City',
  state_province: 'State or province',
  postal_code: 'Postal code',
  country: 'Country',
  phone: 'Phone',
  email: 'Email',
  website: 'Website',
}

const mode = ref('one')
const church = reactive(Object.fromEntries(COLUMNS.map((c) => [c, ''])))
const you = reactive({ name: '', email: '', website_url: '' })
const listText = ref('')
const sending = ref(false)
const sent = ref(0)
const error = ref('')

// A simple CSV reader: commas, quoted values, and a header row naming the columns. Headings
// are matched loosely, so "Church Name" and "church_name" both work.
function parseCsv(text) {
  const rows = []
  let row = [], value = '', quoted = false
  for (let i = 0; i < text.length; i++) {
    const ch = text[i]
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') (value += '"'), i++
      else if (ch === '"') quoted = false
      else value += ch
    } else if (ch === '"') quoted = true
    else if (ch === ',') row.push(value), (value = '')
    else if (ch === '\n' || ch === '\r') {
      if (ch === '\r' && text[i + 1] === '\n') i++
      row.push(value), rows.push(row), (row = []), (value = '')
    } else value += ch
  }
  if (value || row.length) row.push(value), rows.push(row)
  return rows.filter((r) => r.some((v) => v.trim()))
}

const key = (h) => h.trim().toLowerCase().replace(/[^a-z]+/g, '_').replace(/^_|_$/g, '')
const ALIASES = { name: 'church_name', church: 'church_name', pastor: 'pastor_name', state: 'state_province', province: 'state_province', zip: 'postal_code', postcode: 'postal_code', address: 'address_line', street: 'address_line' }

const parsed = computed(() => {
  const rows = parseCsv(listText.value)
  if (rows.length < 2) return { churches: [], unknown: [] }
  const header = rows[0].map((h) => ALIASES[key(h)] || key(h))
  const unknown = header.filter((h) => h && !COLUMNS.includes(h))
  const churches = rows.slice(1).map((r) => Object.fromEntries(header.map((h, i) => [h, (r[i] || '').trim()])))
  return { churches: churches.filter((c) => c.church_name), unknown }
})

function readFile(event) {
  const file = event.target.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => (listText.value = String(reader.result || ''))
  reader.readAsText(file)
}

function template() {
  const csv = `${COLUMNS.join(',')}\nGrace Baptist Church,John Smith,12 Main St,Springfield,Ohio,45501,United States,555-0100,office@example.org,https://example.org\n`
  const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }))
  Object.assign(document.createElement('a'), { href: url, download: 'churches.csv' }).click()
  URL.revokeObjectURL(url)
}

async function submit() {
  error.value = ''
  const churches = mode.value === 'one' ? [{ ...church }] : parsed.value.churches
  if (!churches.length || !churches[0].church_name) {
    error.value = mode.value === 'one' ? 'Add the church’s name.' : 'Add a list with a church_name column and at least one church.'
    return
  }
  sending.value = true
  try {
    const res = await call('missionsit.api.web.submit_churches', {
      churches,
      submitter_name: you.name,
      submitter_email: you.email,
      website_url: you.website_url,
    })
    sent.value = res.received
    COLUMNS.forEach((c) => (church[c] = ''))
    listText.value = ''
  } catch (err) {
    error.value = err?.messages?.[0] || err?.message || 'The churches could not be sent. Try again.'
  } finally {
    sending.value = false
  }
}

const input = 'w-full rounded-4 border border-ink/15 bg-white px-3 py-2 text-[15px] text-ink placeholder:text-ink-soft/60 focus:border-airmail focus:outline-none focus:ring-2 focus:ring-airmail/20'
</script>

<template>
  <section class="rounded-7 border border-ink/10 p-5 sm:p-7" aria-labelledby="submit-title">
    <h2 id="submit-title" class="heading t-h2">Add a church</h2>
    <p class="mt-2 max-w-xl text-ink-soft">
      Know a church that is missing? Send it in, or send a whole list. Someone on our team checks each one before it appears on the map.
    </p>

    <div v-if="sent" class="mt-6 rounded-6 bg-sage-tint p-5" role="status">
      <p class="font-semibold text-sage">
        {{ sent === 1 ? 'Thank you. The church is waiting for review.' : `Thank you. ${sent} churches are waiting for review.` }}
      </p>
      <button type="button" class="mt-3 text-sm font-semibold text-airmail hover:underline" @click="sent = 0">Add another</button>
    </div>

    <form v-else class="mt-6 grid gap-5" @submit.prevent="submit">
      <div class="inline-flex justify-self-start rounded-full border border-ink/10 p-1" role="radiogroup" aria-label="What to add">
        <button
          v-for="m in [['one', 'One church'], ['list', 'A list of churches']]"
          :key="m[0]"
          type="button"
          role="radio"
          :aria-checked="mode === m[0]"
          class="rounded-full px-4 py-1.5 text-sm font-medium"
          :class="mode === m[0] ? 'bg-airmail text-white' : 'text-ink-soft hover:text-ink'"
          @click="mode = m[0]"
        >
          {{ m[1] }}
        </button>
      </div>

      <div v-if="mode === 'one'" class="grid gap-4 sm:grid-cols-2">
        <label v-for="c in COLUMNS" :key="c" class="grid gap-1.5 text-sm font-medium" :class="{ 'sm:col-span-2': c === 'church_name' || c === 'address_line' }">
          <span>{{ HEADINGS[c] }}<span v-if="c === 'church_name'" class="text-ink-soft"> (required)</span></span>
          <input v-model="church[c]" :class="input" :type="c === 'email' ? 'email' : c === 'website' ? 'url' : 'text'" :required="c === 'church_name'" maxlength="140" />
        </label>
      </div>

      <div v-else class="grid gap-3">
        <p class="text-sm text-ink-soft">
          Paste a spreadsheet saved as CSV, or upload the file. The first row names the columns; only <strong class="text-ink">church_name</strong> is required.
          <button type="button" class="font-semibold text-airmail hover:underline" @click="template">Download a template</button>.
        </p>
        <label class="grid gap-1.5 text-sm font-medium">
          <span>The list</span>
          <textarea v-model="listText" rows="7" :class="[input, 'font-[inherit]']" placeholder="church_name,city,country&#10;Grace Baptist Church,Springfield,United States" />
        </label>
        <label class="inline-flex cursor-pointer items-center gap-2 justify-self-start text-sm font-semibold text-airmail hover:underline">
          <span class="lucide-upload size-4" aria-hidden="true" />Upload a CSV file
          <input type="file" accept=".csv,text/csv" class="sr-only" @change="readFile" />
        </label>
        <p v-if="parsed.churches.length" class="text-sm text-ink">
          Ready to send {{ parsed.churches.length === 1 ? '1 church' : `${parsed.churches.length} churches` }}<template v-if="parsed.churches.length > 100">. Send at most 100 at a time</template>.
          <span v-if="parsed.unknown.length" class="text-ink-soft">These columns will be left out: {{ parsed.unknown.join(', ') }}.</span>
        </p>
      </div>

      <fieldset class="grid gap-4 border-t border-ink/10 pt-5 sm:grid-cols-2">
        <legend class="mb-2 text-sm font-semibold">About you, so we can ask a question if we need to (optional)</legend>
        <label class="grid gap-1.5 text-sm font-medium">
          <span>Your name</span>
          <input v-model="you.name" :class="input" maxlength="140" autocomplete="name" />
        </label>
        <label class="grid gap-1.5 text-sm font-medium">
          <span>Your email</span>
          <input v-model="you.email" :class="input" type="email" maxlength="140" autocomplete="email" />
        </label>
        <!-- Hidden from people; a bot that fills it in is ignored. -->
        <label class="absolute -left-[9999px]" aria-hidden="true">
          Website <input v-model="you.website_url" tabindex="-1" autocomplete="off" />
        </label>
      </fieldset>

      <p v-if="error" class="text-sm font-medium text-[#C33A3A]" role="alert">{{ error }}</p>
      <button
        type="submit"
        :disabled="sending"
        class="justify-self-start rounded-full bg-airmail px-5 py-3 text-sm font-semibold text-white hover:bg-airmail-dark disabled:opacity-60"
      >
        {{ sending ? 'Sending…' : mode === 'one' ? 'Send the church for review' : 'Send the list for review' }}
      </button>
    </form>
  </section>
</template>
