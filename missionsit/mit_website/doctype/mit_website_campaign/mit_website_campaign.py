# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Campaign: a time-boxed fundraising push toward a goal."""

import frappe
from frappe.model.document import Document


class MitWebsiteCampaign(Document):
	"""A time-boxed fundraising push toward a goal."""

	def validate(self):
		if self.start_date and self.end_date and self.end_date < self.start_date:
			frappe.throw(frappe._("End date must be on or after the start date."))

	def recalculate_amount_raised(self):
		"""Sum linked Donations and store on *amount_raised*."""
		total = (
			frappe.db.get_value(
				"Mit Finances Donation",
				{"campaign": self.name},
				"SUM(amount)",
			)
			or 0
		)
		self.db_set("amount_raised", total, update_modified=False)


def refresh_amount_raised(doc, method=None):
	"""Donation hook: refresh linked Campaign's amount_raised."""
	if not doc.campaign:
		return
	campaign = frappe.get_doc("Mit Website Campaign", doc.campaign)
	campaign.recalculate_amount_raised()
