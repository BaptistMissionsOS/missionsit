<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
import { LoadingIndicator } from 'frappe-ui'

defineProps({ resource: { type: Object, required: true } })
</script>

<template>
  <div v-if="resource.loading && !resource.data" class="grid place-items-center py-24 text-ink-soft">
    <LoadingIndicator class="size-6" />
  </div>
  <div v-else-if="resource.error" class="py-24 text-center">
    <p class="text-ink">This page could not load: {{ resource.error.messages?.[0] || resource.error.message }}</p>
    <button
      type="button"
      class="mt-4 rounded-full border border-ink/15 px-4 py-2 text-sm font-medium hover:border-airmail"
      @click="resource.reload()"
    >
      Try again
    </button>
  </div>
  <slot v-else-if="resource.data" :data="resource.data" />
</template>
