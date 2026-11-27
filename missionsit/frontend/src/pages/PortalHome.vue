<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
import { createResource } from 'frappe-ui'
import PageState from '@/components/PageState.vue'
import { day, money } from '@/utils'

// The portal layout only renders this once someone is signed in.
const portal = createResource({ url: '/api/method/missionsit.api.web.get_portal', auto: true })

const STATUS_TONE = {
  Accepted: 'bg-sage-tint text-sage',
  Submitted: 'bg-airmail-tint text-airmail',
  'Under Review': 'bg-airmail-tint text-airmail',
  Waitlist: 'bg-harvest-tint text-harvest-dark',
  Rejected: 'bg-mist text-ink-soft',
  Giving: 'bg-sage-tint text-sage',
  Active: 'bg-sage-tint text-sage',
  Promised: 'bg-airmail-tint text-airmail',
  Paused: 'bg-harvest-tint text-harvest-dark',
}
</script>

<template>
  <div>
    <PageState :resource="portal" v-slot="{ data }">
      <h1 class="heading t-h1">Welcome back, {{ data.user.first_name }}</h1>
      <p v-if="data.linked" class="mt-3 t-lead text-ink-soft">
        You have given <strong class="text-ink">{{ money(data.given_this_year) }}</strong> this year. Thank you.
      </p>
      <p v-else class="mt-3 max-w-2xl t-lead text-ink-soft">
        Your gifts are not linked to this account yet. They will appear here once the office links your supporter record to {{ data.user.name }}.
      </p>

      <div class="mt-10 grid gap-10 lg:grid-cols-[minmax(0,1fr)_22rem]">
        <section aria-labelledby="gifts">
          <h2 id="gifts" class="heading t-h2">Your gifts</h2>
          <table v-if="data.donations.length" class="mt-4 w-full text-left text-sm">
            <thead class="border-b border-ink/10 text-ink-soft">
              <tr>
                <th class="py-2 font-medium">Date</th>
                <th class="py-2 font-medium">For</th>
                <th class="py-2 text-right font-medium">Amount</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="d in data.donations" :key="d.name" class="border-b border-ink/10">
                <td class="py-3 tabular-nums">{{ day(d.donation_date) }}</td>
                <td class="py-3">{{ d.missionary_name || d.fund }}</td>
                <td class="py-3 text-right font-semibold tabular-nums">{{ money(d.amount, d.currency) }}</td>
              </tr>
            </tbody>
          </table>
          <p v-else class="mt-4 text-ink-soft">No gifts yet. <RouterLink to="/give" class="font-semibold text-airmail hover:underline">Find a missionary to give to</RouterLink>.</p>
        </section>

        <div class="grid content-start gap-8">
          <section aria-labelledby="monthly">
            <h2 id="monthly" class="heading t-h3">Ongoing giving</h2>
            <ul v-if="data.recurring.length || data.pledges.length" class="mt-3 grid gap-3">
              <li v-for="r in [...data.recurring, ...data.pledges]" :key="r.name" class="rounded-4 border border-ink/10 p-4">
                <div class="flex items-center justify-between gap-3">
                  <span class="font-semibold">{{ money(r.amount, r.currency) }} {{ (r.frequency || '').toLowerCase() }}</span>
                  <span class="rounded-full px-2 py-0.5 text-xs font-medium" :class="STATUS_TONE[r.status]">{{ r.status }}</span>
                </div>
                <p class="mt-1 text-sm text-ink-soft">
                  For {{ r.missionary_name }}<template v-if="r.next_payment_date">, next on {{ day(r.next_payment_date) }}</template>
                </p>
              </li>
            </ul>
            <p v-else class="mt-3 text-sm text-ink-soft">You have no monthly gifts or pledges.</p>
          </section>

          <section aria-labelledby="applications">
            <h2 id="applications" class="heading t-h3">Trip applications</h2>
            <ul v-if="data.applications.length" class="mt-3 grid gap-3">
              <li v-for="a in data.applications" :key="a.name" class="flex items-center justify-between gap-3 rounded-4 border border-ink/10 p-4">
                <span>
                  <span class="block font-semibold">{{ a.trip }}</span>
                  <span class="text-sm text-ink-soft">Applied {{ day(a.application_date) }}</span>
                </span>
                <span class="rounded-full px-2 py-0.5 text-xs font-medium" :class="STATUS_TONE[a.status]">{{ a.status }}</span>
              </li>
            </ul>
            <p v-else class="mt-3 text-sm text-ink-soft">
              No applications. <RouterLink to="/portal/trips" class="font-semibold text-airmail hover:underline">See upcoming trips</RouterLink>.
            </p>
          </section>
        </div>
      </div>
    </PageState>
  </div>
</template>
