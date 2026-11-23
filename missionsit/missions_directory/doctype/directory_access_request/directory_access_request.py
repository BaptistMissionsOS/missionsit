# Copyright (c) 2026, BaptistMissionsOS and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class DirectoryAccessRequest(Document):
	def validate(self):
		# A missionary files the request; only an admin can move it
		# to Approved or Rejected. The directory's shared data was
		# gathered by missionaries' own labor, so access to the full
		# profiles is granted, never assumed.
		before = self.get_doc_before_save()
		old_status = before.status if before else "Pending"
		if self.status != old_status and self.status in ("Approved", "Rejected"):
			roles = frappe.get_roles(frappe.session.user)
			if "System Manager" not in roles and "Organization Admin" not in roles:
				frappe.throw(_("Only an admin can approve or reject an access request."))
			self.reviewed_by = frappe.session.user
			self.reviewed_on = now_datetime()
