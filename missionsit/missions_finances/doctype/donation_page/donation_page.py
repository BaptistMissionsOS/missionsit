# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Donation Page: a public fundraising page for a missionary or fund."""

import re

import frappe
from frappe.model.document import Document


SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class DonationPage(Document):
	"""A public fundraising page for a missionary or fund."""

	def validate(self):
		self._ensure_slug()
		if not SLUG_PATTERN.match(self.slug):
			frappe.throw(
				frappe._("Slug {0} must contain only lowercase letters, numbers and hyphens.").format(self.slug)
			)
		if self.minimum_amount and self.minimum_amount < 0:
			frappe.throw(frappe._("Minimum amount cannot be negative."))

	def _ensure_slug(self):
		"""Derive a slug from the title when not set."""
		if self.slug:
			self.slug = self.slug.strip().lower()
			return
		base = re.sub(r"[^a-z0-9]+", "-", (self.title or "").lower()).strip("-")
		self.slug = base or frappe.generate_hash(length=8)


def get_permission_query_conditions(user: str) -> str:
	"""Limit Missionary role users to pages for their own missionary."""
	if "Missionary" not in frappe.get_roles(user):
		return ""
	missionary = frappe.db.get_value("Missions Missionary", {"user": user}, "name")
	if not missionary:
		return "1=0"
	return f"`tabDonation Page`.`missionary` = {frappe.db.escape(missionary)}"


def has_permission(doc, user: str, permission_type: str = "read") -> bool:
	"""Allow Missionary role only for records linked to their missionary."""
	if "System Manager" in frappe.get_roles(user):
		return True
	missionary = frappe.db.get_value("Missions Missionary", {"user": user}, "name")
	return doc.missionary == missionary
