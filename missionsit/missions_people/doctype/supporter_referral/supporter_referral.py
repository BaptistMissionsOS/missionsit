# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Supporter Referral: tracks who referred a supporter to the missionary."""

from frappe.model.document import Document


class SupporterReferral(Document):
	"""Tracks who referred a supporter to the missionary."""

	def validate(self):
		if self.supporter == self.referred_by:
			import frappe
			frappe.throw(frappe._("A supporter cannot refer themselves."))
