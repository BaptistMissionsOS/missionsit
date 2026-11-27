// This source code is freely given for the sake of the gospel (Matthew 10:8)
// and is licensed under MIT No Attribution (MIT-0).

import { createResource } from 'frappe-ui'

const API = '/api/method/missionsit.api.web'

// Settings and the signed-in user, shared by every page.
export const site = createResource({ url: `${API}.get_site`, auto: true })

export function pageResource(method, params) {
  return createResource({ url: `${API}.${method}`, params, auto: true })
}
