# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Recurring Donation: a scheduled gift that repeats on a frequency."""

import frappe
from frappe.model.document import Document
from frappe.utils import add_months, getdate, today


FREQUENCY_TO_MONTHS = {"Monthly": 1, "Quarterly": 3, "Annual": 12}


class RecurringDonation(Document):
	"""A scheduled gift that repeats on a frequency."""

	def validate(self):
		if self.amount and self.amount <= 0:
			frappe.throw(frappe._("Recurring donation amount must be greater than zero."))
		self._sync_missionary_from_supporter()
		if not self.next_payment_date:
			self.next_payment_date = self.start_date

	def _sync_missionary_from_supporter(self):
		"""Set missionary from the supporter record when not already set."""
		if not self.missionary and self.supporter:
			self.missionary = frappe.db.get_value("Supporter", self.supporter, "missionary")

	def advance_next_payment(self):
		"""Advance *next_payment_date* by one period and save."""
		if self.status != "Active":
			return
		months = FREQUENCY_TO_MONTHS.get(self.frequency, 1)
		base = getdate(self.next_payment_date or today())
		self.next_payment_date = add_months(base, months)
		self.save(ignore_permissions=True)


def advance_due_recurring_donations():
	"""Scheduled daily job: nudge Recurring Donations whose next_payment_date has passed."""
	due = frappe.get_all(
		"Recurring Donation",
		filters={"status": "Active", "next_payment_date": ["<=", today()]},
		pluck="name",
	)
	for name in due:
		doc = frappe.get_doc("Recurring Donation", name)
		doc.advance_next_payment()


def get_permission_query_conditions(user: str) -> str:
	"""Limit Missionary role users to recurring donations for their own missionary."""
	if "Missionary" not in frappe.get_roles(user):
		return ""
	missionary = frappe.db.get_value("Missionary", {"user": user}, "name")
	if not missionary:
		return "1=0"
	return f"`tabRecurring Donation`.`missionary` = {frappe.db.escape(missionary)}"


def has_permission(doc, user: str, permission_type: str = "read") -> bool:
	"""Allow Missionary role only for records linked to their missionary."""
	if "System Manager" in frappe.get_roles(user):
		return True
	missionary = frappe.db.get_value("Missionary", {"user": user}, "name")
	return doc.missionary == missionary
