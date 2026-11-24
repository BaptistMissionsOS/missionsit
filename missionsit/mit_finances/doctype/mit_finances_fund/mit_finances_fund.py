# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Fund: a named bucket that donations and pledges target."""

import frappe
from frappe.model.document import Document


class MitFinancesFund(Document):
	"""A named bucket that donations and pledges target."""

	def validate(self):
		if self.is_default:
			self._clear_other_defaults()

	def _clear_other_defaults(self):
		"""Ensure only one fund is marked default per missionary (or globally)."""
		filters = {"is_default": 1, "name": ["!=", self.name]}
		if self.missionary:
			filters["missionary"] = self.missionary
		frappe.db.set_value("Mit Finances Fund", filters, "is_default", 0)
