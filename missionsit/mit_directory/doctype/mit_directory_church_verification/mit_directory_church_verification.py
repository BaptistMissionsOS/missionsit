# Copyright (c) 2026, BaptistMissionsOS and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from missionsit.mit_directory.doctype.mit_directory_church.mit_directory_church import (
	has_full_directory_access,
	own_church_names,
)


class MitDirectoryChurchVerification(Document):
	def validate(self):
		# Verifying a church is contributing to the shared profiles:
		# limited to admins, approved missionaries, and a
		# missionary's own churches.
		user = frappe.session.user
		if user == "Administrator" or has_full_directory_access(user):
			return
		if self.church in own_church_names(user):
			return
		frappe.throw(_("Only approved missionaries can verify church information."))

	def after_insert(self):
		# A verification is a dated record, not just a timestamp
		# overwritten on the church: the church keeps the latest
		# verification's stamp, and this record stays as the audit
		# trail of who confirmed what, and when.
		if not self.church:
			return
		values = {
			"last_verified": self.verified_on,
			"verified_by": self.verified_by,
		}
		if self.outcome == "Closed":
			values["status"] = "Closed"
		elif self.outcome in ("Confirmed Active", "Details Changed", "Moved"):
			values["status"] = "Active"
		frappe.db.set_value("Mit Directory Church", self.church, values)
