# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Trip Application: a request from someone who wants to join a Trip."""

import frappe
from frappe.model.document import Document


class TripApplication(Document):
	"""A request from someone who wants to join a Trip."""

	def validate(self):
		if self.email:
			frappe.utils.validate_email_address(self.email, throw=True)

	def on_update(self):
		if self.has_value_changed("status") and self.status == "Accepted":
			self._promote_to_participant()

	def _promote_to_participant(self):
		"""Create a Trip Participant for this application when accepted."""
		exists = frappe.db.exists(
			"Trip Participant",
			{"trip": self.trip, "email": self.email},
		)
		if exists:
			return
		participant = frappe.get_doc(
			{
				"doctype": "Trip Participant",
				"trip": self.trip,
				"full_name": self.applicant_name,
				"email": self.email,
				"phone": self.phone,
				"status": "Accepted",
			}
		)
		participant.insert(ignore_permissions=True)
		frappe.msgprint(
			frappe._("Created Trip Participant {0} for {1}.").format(participant.name, self.applicant_name),
			alert=True,
		)
