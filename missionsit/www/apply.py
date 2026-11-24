# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Context for /apply/<trip>: resolves a Trip and offers a public application form."""

import frappe


no_cache = 1


def get_context(context):
	trip_name = frappe.form_dict.get("trip") or (frappe.request.path.split("/apply/", 1)[-1] if frappe.request else "")
	if not trip_name:
		frappe.local.flags.redirect_location = "/"
		raise frappe.Redirect
	trip = frappe.db.get_value(
		"Mit Trip",
		{"name": trip_name, "status": ["in", ["Open", "Planning"]]},
		["name", "trip_name", "destination", "start_date", "end_date", "description"],
		as_dict=True,
	)
	if not trip:
		raise frappe.DoesNotExistError(frappe._("Trip not found or no longer accepting applications."))
	context.no_cache = 1
	context.trip = trip
	context.title = trip.trip_name
	return context


@frappe.whitelist(allow_guest=True)
def submit_application(
	trip: str,
	applicant_name: str,
	email: str,
	phone: str = "",
	date_of_birth: str = "",
	motivation: str = "",
	experience: str = "",
	emergency_contact: str = "",
) -> dict:
	"""Insert a Trip Application from a public form. Returns *{name}*."""
	if not frappe.db.exists("Mit Trip", {"name": trip, "status": ["in", ["Open", "Planning"]]}):
		frappe.throw(frappe._("Trip {0} is not accepting applications.").format(trip))
	application = frappe.get_doc(
		{
			"doctype": "Mit Trip Application",
			"trip": trip,
			"applicant_name": applicant_name,
			"email": email,
			"phone": phone,
			"date_of_birth": date_of_birth or None,
			"motivation": motivation,
			"experience": experience,
			"emergency_contact": emergency_contact,
			"application_date": frappe.utils.today(),
			"status": "Submitted",
		}
	)
	application.insert(ignore_permissions=True)
	return {"name": application.name}
