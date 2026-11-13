# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Trip Participant: a person going on a Trip, with a personal fundraising goal."""

import frappe
from frappe.model.document import Document


class TripParticipant(Document):
	"""A person going on a Trip, with a personal fundraising goal."""

	def validate(self):
		if not self.supporter and not self.full_name:
			frappe.throw(frappe._("Provide a Supporter or a Full Name."))
		self._sync_from_supporter()
		if self.email:
			frappe.utils.validate_email_address(self.email, throw=True)

	def _sync_from_supporter(self):
		"""Copy name, email and phone from the linked Supporter when empty."""
		if not self.supporter:
			return
		supporter = frappe.db.get_value(
			"Supporter",
			self.supporter,
			["supporter_name", "email", "phone"],
			as_dict=True,
		)
		if not supporter:
			return
		if not self.full_name:
			self.full_name = supporter.supporter_name
		if not self.email:
			self.email = supporter.email
		if not self.phone:
			self.phone = supporter.phone

	def recalculate_amount_raised(self):
		"""Sum linked Donations and store on *amount_raised*."""
		total = (
			frappe.db.get_value(
				"Donation",
				{"trip_participant": self.name},
				"SUM(amount)",
			)
			or 0
		)
		self.db_set("amount_raised", total, update_modified=False)


def refresh_amount_raised(doc, method=None):
	"""Donation hook: refresh linked Trip Participant's amount_raised."""
	if not doc.trip_participant:
		return
	participant = frappe.get_doc("Trip Participant", doc.trip_participant)
	participant.recalculate_amount_raised()
