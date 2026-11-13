# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Church: a sending or supporting church that partners with missionaries."""

import frappe
from frappe.model.document import Document


class Church(Document):
	"""A sending or supporting church that partners with missionaries."""

	def validate(self):
		if self.email:
			frappe.utils.validate_email_address(self.email, throw=True)
