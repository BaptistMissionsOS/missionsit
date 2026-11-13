# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Ministry Task: an action item in the supporter relationship pipeline."""

import frappe
from frappe.model.document import Document


class MinistryTask(Document):
	"""An action item in the supporter relationship pipeline."""

	def validate(self):
		self._sync_missionary_from_supporter()
		if self.status == "Completed" and not self.completed_on:
			self.completed_on = frappe.utils.now()

	def _sync_missionary_from_supporter(self):
		"""Set missionary from the supporter record when not already set."""
		if not self.missionary and self.supporter:
			self.missionary = frappe.db.get_value("Supporter", self.supporter, "missionary")


def get_permission_query_conditions(user: str) -> str:
	"""Limit Missionary role users to tasks for their own missionary."""
	if "Missionary" not in frappe.get_roles(user):
		return ""
	missionary = frappe.db.get_value("Missionary", {"user": user}, "name")
	if not missionary:
		return "1=0"
	return f"`tabMinistry Task`.`missionary` = {frappe.db.escape(missionary)}"


def has_permission(doc, user: str, permission_type: str = "read") -> bool:
	"""Allow Missionary role only for records linked to their missionary."""
	if "System Manager" in frappe.get_roles(user):
		return True
	missionary = frappe.db.get_value("Missionary", {"user": user}, "name")
	return doc.missionary == missionary
