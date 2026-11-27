<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import AccountMenu from './AccountMenu.vue'
import { site } from '@/data'
import { links } from '@/utils'

const nav = [
  { label: 'Missionaries', to: '/missionaries' },
  { label: 'Church Directory', to: '/directory' },
  { label: 'Give', to: '/give' },
]
const open = ref(false)
const route = useRoute()
watch(() => route.fullPath, () => (open.value = false))
</script>

<template>
  <header class="sticky top-0 z-20 border-b border-ink/10 bg-white/95 backdrop-blur">
    <div class="page flex h-16 items-center gap-4 md:gap-6">
      <RouterLink to="/" class="flex min-w-0 items-center gap-2.5" aria-label="Home">
        <span class="grid size-8 shrink-0 place-items-center rounded-full bg-airmail text-white" aria-hidden="true">
          <span class="lucide-globe size-[18px]" />
        </span>
        <span class="heading t-h4 truncate">{{ site.data?.title || 'Missions' }}</span>
      </RouterLink>

      <nav class="ml-4 hidden items-center gap-1 md:flex" aria-label="Main">
        <RouterLink
          v-for="item in nav"
          :key="item.to"
          :to="item.to"
          class="rounded-3 px-3 py-2 text-sm font-medium text-ink-soft transition-colors hover:text-ink"
          active-class="!text-airmail"
        >
          {{ item.label }}
        </RouterLink>
      </nav>

      <div class="ml-auto flex shrink-0 items-center gap-3">
        <RouterLink
          to="/give"
          class="hidden rounded-full bg-harvest px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-harvest-dark sm:inline-flex"
        >
          Give
        </RouterLink>
        <AccountMenu v-if="site.data?.user" :user="site.data.user" />
        <a
          v-else-if="site.data"
          :href="links.signIn()"
          class="whitespace-nowrap rounded-full border border-ink/15 px-4 py-2 text-sm font-medium hover:border-airmail hover:text-airmail"
        >
          Sign in
        </a>
        <button
          type="button"
          class="grid size-9 place-items-center rounded-3 hover:bg-mist md:hidden"
          :aria-expanded="open"
          aria-controls="mobile-nav"
          aria-label="Menu"
          @click="open = !open"
        >
          <span :class="open ? 'lucide-x' : 'lucide-menu'" class="size-5" aria-hidden="true" />
        </button>
      </div>
    </div>
    <nav v-if="open" id="mobile-nav" class="page border-t border-ink/10 py-2 md:hidden" aria-label="Main">
      <RouterLink
        v-for="item in nav"
        :key="item.to"
        :to="item.to"
        class="block rounded-3 px-2 py-3 text-base font-medium"
        active-class="text-airmail"
      >
        {{ item.label }}
      </RouterLink>
    </nav>
  </header>
</template>
