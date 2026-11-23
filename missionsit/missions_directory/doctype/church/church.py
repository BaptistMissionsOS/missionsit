# Copyright (c) 2026, BaptistMissionsOS and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Church(Document):
	def validate(self):
		# Completeness flags are computed, never hand-maintained:
		# the directory shows at a glance which contact facts a
		# church record actually carries.
		self.has_phone = 1 if self.phone else 0
		self.has_email = 1 if self.email else 0
		self.has_website = 1 if self.website else 0
		self.has_location = 1 if self.location else 0
		self._guard_shared_contributions()

	def _guard_shared_contributions(self):
		# Comments and accommodation listings on a profile are the
		# shared data missionaries gathered by their own labor.
		# Adding them is limited to admins, approved missionaries,
		# and a missionary's own churches. (Church and agency
		# accounts keep their own profile, and are not the
		# Missionary role, so they are not caught by this guard.)
		user = frappe.session.user
		if user == "Administrator" or "Missionary" not in frappe.get_roles(user):
			return
		if has_full_directory_access(user) or self.name in own_church_names(user):
			return
		before = self.get_doc_before_save()
		for table in ("public_notes", "accommodations"):
			old = {row.name for row in (getattr(before, table, None) or [])}
			if any(not row.name or row.name not in old for row in getattr(self, table, [])):
				frappe.throw(
					_("Only approved missionaries can add comments or accommodations to a church profile.")
				)


def _missionary_for(user):
	return frappe.db.get_value(
		"Missions Missionary",
		{"user": user},
		["name", "status", "support_model", "is_verified", "sending_church"],
		as_dict=True,
	)


def own_church_names(user):
	"""The churches a missionary may always see in full: his sending
	church, and the church(es) he has planted (Ministry Projects of
	type Church Plant that name a Church)."""
	missionary = _missionary_for(user)
	if not missionary:
		return set()
	names = set()
	if missionary.sending_church:
		names.add(missionary.sending_church)
	for project in frappe.get_all(
		"Ministry Project",
		filters={"missionary": missionary.name, "project_type": "Church Plant"},
		fields=["church"],
	):
		if project.church:
			names.add(project.church)
	return names


def has_full_directory_access(user):
	"""Full church profiles are for admins and for missionaries
	whose Directory Access Request an admin has approved. The
	shared data was collected by missionaries' hard labor, so it
	is not open by default — a tentmaker (or any missionary) asks,
	and an admin grants it."""
	roles = frappe.get_roles(user)
	if "System Manager" in roles or "Organization Admin" in roles:
		return True
	missionary = _missionary_for(user)
	if not missionary:
		return False
	return bool(
		frappe.db.exists(
			"Directory Access Request",
			{"missionary": missionary.name, "status": "Approved"},
		)
	)


def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user
	if has_full_directory_access(user):
		return ""
	if "Missionary" not in frappe.get_roles(user):
		# Church and agency accounts are scoped by User Permissions
		# naming their church or their organization's churches.
		return ""
	own = own_church_names(user)
	if not own:
		return "1=0"
	quoted = ", ".join(frappe.db.escape(name) for name in own)
	return f"`tabChurch`.`name` in ({quoted})"


def has_permission(doc, user=None, permission_type=None):
	if not user:
		user = frappe.session.user
	if has_full_directory_access(user):
		return True
	if "Missionary" not in frappe.get_roles(user):
		return None
	return doc.name in own_church_names(user)
