# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Daily scheduler for Email Campaigns whose scheduled_date has arrived."""

import frappe
from frappe.utils import now


def send_due_campaigns():
	"""Send every Scheduled campaign whose scheduled_date has passed."""
	due = frappe.get_all(
		"Mit Correspondence Email Campaign",
		filters={"status": "Scheduled", "scheduled_date": ["<=", now()]},
		pluck="name",
	)
	for name in due:
		doc = frappe.get_doc("Mit Correspondence Email Campaign", name)
		try:
			doc.send_now()
		except Exception:
			frappe.log_error(frappe.get_traceback(), f"Email Campaign {name} failed")
