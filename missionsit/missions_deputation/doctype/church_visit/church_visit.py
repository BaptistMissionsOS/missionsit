# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Church Visit: a deputation or support visit from a missionary to a church."""

import frappe
from frappe.model.document import Document


class ChurchVisit(Document):
	"""A deputation or support visit from a missionary to a church."""

	def validate(self):
		if self.outcome == "Follow-up Needed" and not self.follow_up_task:
			self._create_follow_up_task()

	def _create_follow_up_task(self):
		"""Create a Ministry Task for follow-up and link it back."""
		task = frappe.get_doc(
			{
				"doctype": "Ministry Task",
				"title": frappe._("Follow up with {0}").format(self.church),
				"task_type": "Visit",
				"tag": "Follow-up",
				"missionary": self.missionary,
				"due_date": frappe.utils.add_days(frappe.utils.today(), 7),
				"status": "Open",
				"priority": "Medium",
			}
		)
		task.insert(ignore_permissions=True)
		self.follow_up_task = task.name


def get_permission_query_conditions(user: str) -> str:
	"""Limit Missionary role users to visits for their own missionary."""
	if "Missionary" not in frappe.get_roles(user):
		return ""
	missionary = frappe.db.get_value("Missions Missionary", {"user": user}, "name")
	if not missionary:
		return "1=0"
	return f"`tabChurch Visit`.`missionary` = {frappe.db.escape(missionary)}"


def has_permission(doc, user: str, permission_type: str = "read") -> bool:
	"""Allow Missionary role only for records linked to their missionary."""
	if "System Manager" in frappe.get_roles(user):
		return True
	missionary = frappe.db.get_value("Missions Missionary", {"user": user}, "name")
	return doc.missionary == missionary
