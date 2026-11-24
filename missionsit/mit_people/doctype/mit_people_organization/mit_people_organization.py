# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Organization: a sending church, agency, mission board, or other supporting organization."""

import frappe
from frappe.model.document import Document


class MitPeopleOrganization(Document):
	"""A sending church, agency, mission board, or other supporting organization."""

	def validate(self):
		if self.email:
			frappe.utils.validate_email_address(self.email, throw=True)
