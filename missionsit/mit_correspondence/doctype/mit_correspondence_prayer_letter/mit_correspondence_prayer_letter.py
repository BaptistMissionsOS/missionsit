# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Prayer Letter: a newsletter or update letter sent to supporters."""

from frappe.model.document import Document


class MitCorrespondencePrayerLetter(Document):
	"""A newsletter or update letter sent to supporters."""


def get_permission_query_conditions(user: str) -> str:
	"""Limit Missionary role users to prayer letters for their own missionary."""
	import frappe

	if "System Manager" in frappe.get_roles(user):
		return ""
	if "Missionary" not in frappe.get_roles(user):
		return ""
	missionary = frappe.db.get_value("Mit People Missionary", {"user": user}, "name")
	if not missionary:
		return "1=0"
	return f"`tabMit Correspondence Prayer Letter`.`missionary` = {frappe.db.escape(missionary)}"


def has_permission(doc, user: str, permission_type: str = "read") -> bool:
	"""Allow Missionary role only for records linked to their missionary."""
	import frappe

	if "System Manager" in frappe.get_roles(user):
		return True
	missionary = frappe.db.get_value("Mit People Missionary", {"user": user}, "name")
	return doc.missionary == missionary
