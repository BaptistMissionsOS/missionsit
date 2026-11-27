<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
import { computed } from 'vue'
import { money, percent } from '@/utils'

const props = defineProps({
  raised: { type: Number, default: 0 },
  goal: { type: Number, default: 0 },
  currency: { type: String, default: '' },
})
const pct = computed(() => percent(props.raised, props.goal))
</script>

<template>
  <div>
    <div class="flex items-baseline justify-between gap-3 text-sm">
      <span class="font-semibold text-ink">{{ money(raised, currency) }} given</span>
      <span v-if="goal" class="text-ink-soft">{{ pct }}% of {{ money(goal, currency) }}</span>
    </div>
    <div
      v-if="goal"
      class="mt-2 h-2 overflow-hidden rounded-full bg-mist"
      role="progressbar"
      :aria-valuenow="pct"
      aria-valuemin="0"
      aria-valuemax="100"
    >
      <div class="h-full rounded-full bg-sage" :style="{ width: `${pct}%` }" />
    </div>
  </div>
</template>
