# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Donation: a recorded gift from a supporter to a missionary fund."""

import frappe
from frappe.model.document import Document


class MitFinancesDonation(Document):
	"""A recorded gift from a supporter to a missionary fund."""

	def validate(self):
		if self.amount and self.amount <= 0:
			frappe.throw(frappe._("Donation amount must be greater than zero."))
		self._sync_missionary_from_supporter()

	def _sync_missionary_from_supporter(self):
		"""Set missionary from the supporter record when not already set."""
		if not self.missionary and self.supporter:
			self.missionary = frappe.db.get_value("Mit People Supporter", self.supporter, "missionary")


def mark_first_gift(doc, method=None):
	"""Set is_first_gift when this is the supporter's first donation. Runs on before_insert."""
	prior = frappe.db.count("Mit Finances Donation", {"supporter": doc.supporter})
	doc.is_first_gift = 1 if prior == 0 else 0


def create_thank_you_task(doc, method=None):
	"""Create a Thank You Ministry Task when a first gift is recorded. Runs on after_insert."""
	if not doc.is_first_gift:
		return
	task = frappe.get_doc(
		{
			"doctype": "Mit Correspondence Ministry Task",
			"title": frappe._("Thank {0} for their first gift").format(doc.supporter),
			"task_type": "Thank You",
			"tag": "Thank",
			"supporter": doc.supporter,
			"missionary": doc.missionary,
			"due_date": frappe.utils.add_days(frappe.utils.today(), 3),
			"status": "Open",
			"priority": "High",
		}
	)
	task.insert(ignore_permissions=True)


def get_permission_query_conditions(user: str) -> str:
	"""Limit Missionary role users to donations for their own missionary."""
	if "System Manager" in frappe.get_roles(user):
		return ""
	if "Missionary" not in frappe.get_roles(user):
		return ""
	missionary = frappe.db.get_value("Mit People Missionary", {"user": user}, "name")
	if not missionary:
		return "1=0"
	return f"`tabMit Finances Donation`.`missionary` = {frappe.db.escape(missionary)}"


def has_permission(doc, user: str, permission_type: str = "read") -> bool:
	"""Allow Missionary role only for records linked to their missionary."""
	if "System Manager" in frappe.get_roles(user):
		return True
	missionary = frappe.db.get_value("Mit People Missionary", {"user": user}, "name")
	return doc.missionary == missionary
