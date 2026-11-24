# Copyright (c) 2026, BaptistMissionsOS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class MitDirectoryChurchSubmission(Document):
	def on_update(self):
		# Nothing reaches the public directory directly: a submission
		# becomes a Church only when a reviewer marks it Approved.
		# The new record starts as Unknown — being listed is not the
		# same as being verified; verification is a separate act.
		if self.status == "Approved" and not self.church:
			church = frappe.get_doc(
				{
					"doctype": "Mit Directory Church",
					"church_name": self.church_name,
					"pastor_name": self.pastor_name,
					"affiliation": self.affiliation,
					"country": self.country,
					"address_line": self.address_line,
					"city": self.city,
					"state_province": self.state_province,
					"postal_code": self.postal_code,
					"phone": self.phone,
					"email": self.email,
					"website": self.website,
					"service_times": self.service_times,
					"language": self.language,
					"status": "Unknown",
					"data_source": self.source,
				}
			)
			church.insert(ignore_permissions=True)
			frappe.db.set_value(
				"Mit Directory Church Submission",
				self.name,
				{
					"church": church.name,
					"reviewed_by": frappe.session.user,
					"reviewed_on": now_datetime(),
				},
			)
