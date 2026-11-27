// This source code is freely given for the sake of the gospel (Matthew 10:8)
// and is licensed under MIT No Attribution (MIT-0).

// Imported first by main.js. Resources in data.js start fetching as soon as they are imported,
// and ES imports run before main.js's own code, so the fetcher has to be set in a module of
// its own that loads ahead of them.
import { setConfig, frappeRequest } from 'frappe-ui'

setConfig('resourceFetcher', frappeRequest)
