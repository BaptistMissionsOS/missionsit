# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Email Campaign: a bulk email sent to a Supporter Group."""

import frappe
from frappe.model.document import Document


class EmailCampaign(Document):
	"""A bulk email sent to a Supporter Group."""

	def validate(self):
		if self.status == "Scheduled" and not self.scheduled_date:
			frappe.throw(frappe._("Set a Scheduled Date before marking the campaign Scheduled."))

	@frappe.whitelist()
	def send_now(self) -> dict:
		"""Send this campaign to its Supporter Group immediately. Returns a *count* dict."""
		if self.status == "Sent":
			frappe.throw(frappe._("This campaign has already been sent."))
		recipients = self._collect_recipients()
		if not recipients:
			frappe.throw(frappe._("No recipients with email consent in {0}.").format(self.supporter_group))
		for email in recipients:
			frappe.sendmail(
				recipients=[email],
				subject=self.subject or self.title,
				message=self.content or "",
				reference_doctype=self.doctype,
				reference_name=self.name,
			)
		self.db_set("status", "Sent", update_modified=False)
		self.db_set("sent_date", frappe.utils.now(), update_modified=False)
		self.db_set("recipients_count", len(recipients), update_modified=False)
		return {"count": len(recipients)}

	def _collect_recipients(self) -> list[str]:
		"""Return supporter emails for the linked group's missionary, scoped to those with email consent."""
		if not self.supporter_group:
			return []
		group_missionary = frappe.db.get_value("Supporter Group", self.supporter_group, "missionary")
		if not group_missionary:
			return []
		rows = frappe.get_all(
			"Supporter",
			filters={"missionary": group_missionary, "consent_email": 1},
			pluck="email",
		)
		return [row for row in rows if row]
