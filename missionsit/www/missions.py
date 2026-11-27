# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Serves the public web app built from /frontend. missions.html is written by `yarn build`."""

import frappe

no_cache = 1


def get_context(context):
	csrf_token = frappe.sessions.get_csrf_token()
	# The token has to be stored now: the page is not cached, and the app posts with it.
	frappe.db.commit()
	context.boot = {
		"csrf_token": csrf_token,
		"site_name": frappe.local.site,
	}
	return context
