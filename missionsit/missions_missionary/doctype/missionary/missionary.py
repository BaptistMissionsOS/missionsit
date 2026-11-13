# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Missionary: the central record for a missionary's profile and support goal."""

import frappe
from frappe.model.document import Document


class Missionary(Document):
	"""The central record for a missionary's profile and support goal."""

	def validate(self):
		if self.monthly_support_goal and self.monthly_support_goal < 0:
			frappe.throw(frappe._("Monthly Support Goal cannot be negative."))


@frappe.whitelist(methods=["GET"])
def get_missionary_for_user(user: str) -> str | None:
	"""Name of the Missionary record linked to *user*, or None. Reads only."""
	return frappe.db.get_value("Missionary", {"user": user}, "name")
