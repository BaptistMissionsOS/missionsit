<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
import { Avatar } from 'frappe-ui'

defineProps({ missionaries: { type: Array, default: () => [] } })
</script>

<template>
  <ul class="grid gap-x-10 border-t border-ink/10 md:grid-cols-2">
    <li v-for="m in missionaries" :key="m.name" class="border-b border-ink/10">
      <RouterLink
        :to="`/missionaries/${encodeURIComponent(m.slug)}`"
        class="group flex items-center gap-4 py-5"
      >
        <img
          v-if="m.image"
          :src="m.image"
          :alt="''"
          class="size-16 shrink-0 rounded-full object-cover"
          loading="lazy"
        />
        <Avatar v-else :label="m.display_name" size="3xl" class="shrink-0" />
        <span class="min-w-0">
          <span class="heading t-h4 block group-hover:text-airmail">{{ m.display_name }}</span>
          <span v-if="m.headline" class="block truncate text-sm text-ink-soft">{{ m.headline }}</span>
          <span class="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
            <span v-if="m.field_country" class="inline-flex items-center gap-1 font-medium text-airmail">
              <span class="lucide-map-pin size-3.5" aria-hidden="true" />{{ m.field_country }}
            </span>
            <span v-if="m.status" class="text-ink-soft">{{ m.status }}</span>
          </span>
        </span>
      </RouterLink>
    </li>
  </ul>
</template>
