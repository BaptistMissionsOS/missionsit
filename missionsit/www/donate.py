# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Context for /donate/<slug>: resolves a Donation Page by slug."""

import frappe


no_cache = 1


def get_context(context):
	slug = frappe.form_dict.get("slug") or (frappe.request.path.split("/donate/", 1)[-1] if frappe.request else "")
	if not slug:
		frappe.local.flags.redirect_location = "/"
		raise frappe.Redirect
	page = frappe.db.get_value(
		"Donation Page",
		{"slug": slug, "is_active": 1},
		["name", "title", "missionary", "fund", "goal_amount", "currency", "description", "thank_you_message", "allow_recurring", "minimum_amount"],
		as_dict=True,
	)
	if not page:
		raise frappe.DoesNotExistError(frappe._("Donation page not found."))
	context.no_cache = 1
	context.page = page
	context.missionary_name = frappe.db.get_value("Missions Missionary", page.missionary, "missionary_name")
	context.title = page.title
	return context
