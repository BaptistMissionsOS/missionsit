# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Trip: a short-term missions trip that participants raise support for."""

import frappe
from frappe.model.document import Document


class MitTrip(Document):
	"""A short-term missions trip that participants raise support for."""

	def validate(self):
		if self.start_date and self.end_date and self.end_date < self.start_date:
			frappe.throw(frappe._("End date must be on or after the start date."))
