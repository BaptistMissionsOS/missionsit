// This source code is freely given for the sake of the gospel (Matthew 10:8)
// and is licensed under MIT No Attribution (MIT-0).

import { createResource } from 'frappe-ui'

const API = '/api/method/missionsit.api.web'

// Settings and the signed-in user, shared by every page.
export const site = createResource({ url: `${API}.get_site`, auto: true })

export function pageResource(method, params) {
  return createResource({ url: `${API}.${method}`, params, auto: true })
}

// Church pins for the map: name and location only (see get_public_map_pins).
// Loaded on the pages that show the map, once, and kept.
export const directory = createResource({
  url: '/api/method/missionsit.mit_directory.api.get_public_map_pins',
})

export function loadDirectory() {
  if (!directory.data && !directory.loading) directory.fetch()
}

export const portalModules = createResource({ url: '/api/method/missionsit.api.portal.get_modules' })
