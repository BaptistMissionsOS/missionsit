<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
// The Member Portal: sign in first, then a sidebar with your giving, trips, and a page for each
// desk module your account can open.
import { watch } from 'vue'
import { site, portalModules } from '@/data'
import { links } from '@/utils'

watch(
  () => site.data?.user,
  (user) => user && !portalModules.data && !portalModules.loading && portalModules.fetch(),
  { immediate: true },
)

// Desk icons this icon set lacks, drawn with the nearest one it has.
const ICON = { 'hands-praying': 'heart' }
const iconOf = (m) => `lucide-${ICON[m.icon] || m.icon || 'folder'}`

const link =
  'flex items-center gap-2.5 rounded-4 px-3 py-2 text-[15px] font-medium text-ink-soft hover:bg-mist hover:text-ink'
const active = '!bg-airmail-tint !text-airmail'
</script>

<template>
  <div class="page pt-10">
    <template v-if="site.data && !site.data.user">
      <h1 class="heading t-h1">Member Portal</h1>
      <p class="t-lead mt-3 max-w-xl text-ink-soft">
        Sign in to see your gifts, monthly giving, trips and applications, and the parts of our work your account is part of.
      </p>
      <a :href="links.signIn($route.fullPath === '/' ? '/missions/portal' : `/missions${$route.fullPath}`)" class="mt-6 inline-flex rounded-full bg-airmail px-5 py-3 text-sm font-semibold text-white hover:bg-airmail-dark">
        Sign in
      </a>
    </template>

    <div v-else-if="site.data" class="grid gap-8 lg:grid-cols-[14rem_minmax(0,1fr)]">
      <nav aria-label="Member Portal" class="-mx-4 overflow-x-auto px-4 lg:mx-0 lg:overflow-visible lg:px-0">
        <ul class="flex gap-1 lg:sticky lg:top-24 lg:grid">
          <li>
            <RouterLink to="/portal" :class="link" :exact-active-class="active">
              <span class="lucide-heart-handshake size-4 shrink-0" aria-hidden="true" /><span class="whitespace-nowrap">My giving</span>
            </RouterLink>
          </li>
          <li>
            <RouterLink to="/portal/trips" :class="link" :active-class="active">
              <span class="lucide-plane size-4 shrink-0" aria-hidden="true" /><span class="whitespace-nowrap">Trips</span>
            </RouterLink>
          </li>
          <li v-if="portalModules.data?.length" class="hidden px-3 pb-1 pt-4 text-xs font-semibold text-ink-soft lg:block" aria-hidden="true">
            Your work
          </li>
          <li v-for="m in portalModules.data || []" :key="m.slug">
            <RouterLink :to="`/portal/${m.slug}`" :class="link" :active-class="active">
              <span :class="iconOf(m)" class="size-4 shrink-0" aria-hidden="true" />
              <span class="whitespace-nowrap">{{ m.title }}</span>
            </RouterLink>
          </li>
        </ul>
      </nav>
      <div class="min-w-0">
        <RouterView />
      </div>
    </div>
  </div>
</template>
