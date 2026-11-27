<!-- This source code is freely given for the sake of the gospel (Matthew 10:8)
     and is licensed under MIT No Attribution (MIT-0). -->
<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Avatar, Dropdown, call } from 'frappe-ui'
import { links } from '@/utils'

const props = defineProps({ user: { type: Object, required: true } })
const router = useRouter()

async function logout() {
  await call('logout')
  window.location.href = '/missions'
}

const options = computed(() => [
  {
    group: props.user.full_name,
    options: [
      { label: 'Member Portal', icon: 'lucide-heart-handshake', onClick: () => router.push('/portal') },
      { label: 'My Account', icon: 'lucide-user-round', onClick: () => (window.location.href = links.account) },
      ...(props.user.is_desk_user
        ? [{ label: 'Switch to desk', icon: 'lucide-layout-grid', onClick: () => (window.location.href = links.desk) }]
        : []),
    ],
  },
  {
    group: 'Session',
    hideLabel: true,
    options: [{ label: 'Logout', icon: 'lucide-log-out', onClick: logout }],
  },
])
</script>

<template>
  <Dropdown :options="options" align="end">
    <template #default="{ open }">
      <button
        type="button"
        class="flex items-center gap-2 rounded-full p-0.5 pr-2 transition-colors hover:bg-mist"
        :class="{ 'bg-mist': open }"
        :aria-label="`Account menu for ${user.full_name}`"
      >
        <Avatar :image="user.image" :label="user.full_name" size="lg" />
        <span class="hidden text-sm font-medium sm:inline">{{ user.first_name }}</span>
        <span class="lucide-chevron-down size-4 text-ink-soft" aria-hidden="true" />
      </button>
    </template>
  </Dropdown>
</template>
