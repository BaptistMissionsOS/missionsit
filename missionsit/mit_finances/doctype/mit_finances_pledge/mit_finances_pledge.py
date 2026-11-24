# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Pledge: a commitment from a supporter to give at a set amount and frequency."""

import frappe
from frappe.model.document import Document


class MitFinancesPledge(Document):
	"""A commitment from a supporter to give at a set amount and frequency."""

	def validate(self):
		if self.amount and self.amount <= 0:
			frappe.throw(frappe._("Pledge amount must be greater than zero."))
		if self.end_date and self.start_date and self.end_date < self.start_date:
			frappe.throw(frappe._("End Date cannot be before Start Date."))
		self._sync_missionary_from_supporter()

	def _sync_missionary_from_supporter(self):
		"""Set missionary from the supporter record when not already set."""
		if not self.missionary and self.supporter:
			self.missionary = frappe.db.get_value("Mit People Supporter", self.supporter, "missionary")


def get_permission_query_conditions(user: str) -> str:
	"""Limit Missionary role users to pledges for their own missionary."""
	if "Missionary" not in frappe.get_roles(user):
		return ""
	missionary = frappe.db.get_value("Mit People Missionary", {"user": user}, "name")
	if not missionary:
		return "1=0"
	return f"`tabPledge`.`missionary` = {frappe.db.escape(missionary)}"


def has_permission(doc, user: str, permission_type: str = "read") -> bool:
	"""Allow Missionary role only for records linked to their missionary."""
	if "System Manager" in frappe.get_roles(user):
		return True
	missionary = frappe.db.get_value("Mit People Missionary", {"user": user}, "name")
	return doc.missionary == missionary
