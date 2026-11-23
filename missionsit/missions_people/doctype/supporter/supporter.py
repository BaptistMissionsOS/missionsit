# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Supporter: a person or family who partners with a missionary in prayer and giving."""

import frappe
from frappe.model.document import Document


class Supporter(Document):
	"""A person or family who partners with a missionary in prayer and giving."""

	def validate(self):
		if self.email:
			frappe.utils.validate_email_address(self.email, throw=True)
		if self.spouse_email:
			frappe.utils.validate_email_address(self.spouse_email, throw=True)
		if self.consent_email and not self.consent_email_date:
			self.consent_email_date = frappe.utils.today()
		if self.consent_mail and not self.consent_mail_date:
			self.consent_mail_date = frappe.utils.today()


def get_permission_query_conditions(user: str) -> str:
	"""Limit Missionary role users to their own missionary's supporters."""
	if "Missionary" not in frappe.get_roles(user):
		return ""
	missionary = frappe.db.get_value("Missions Missionary", {"user": user}, "name")
	if not missionary:
		return "1=0"
	return f"`tabSupporter`.`missionary` = {frappe.db.escape(missionary)}"


def has_permission(doc, user: str, permission_type: str = "read") -> bool:
	"""Allow Missionary role only for records linked to their missionary."""
	if "System Manager" in frappe.get_roles(user):
		return True
	missionary = frappe.db.get_value("Missions Missionary", {"user": user}, "name")
	return doc.missionary == missionary
