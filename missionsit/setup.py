# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""After-install setup: seeds default Partnership Stage and Fund records."""

import frappe


def after_install():
	"""Seed starter data after app install."""
	_seed_partnership_stages()
	_seed_default_fund()


def _seed_partnership_stages():
	stages = [
		{"stage_name": "Contact", "stage_order": 1, "color": "#6c757d", "probability": 10, "is_active": 1},
		{"stage_name": "Appointment", "stage_order": 2, "color": "#17a2b8", "probability": 25, "is_active": 1},
		{"stage_name": "Presentation", "stage_order": 3, "color": "#ffc107", "probability": 50, "is_active": 1},
		{"stage_name": "Partner", "stage_order": 4, "color": "#28a745", "probability": 100, "is_active": 1},
		{"stage_name": "Lapsed", "stage_order": 5, "color": "#dc3545", "probability": 0, "is_active": 1},
	]
	for s in stages:
		if not frappe.db.exists("Partnership Stage", s["stage_name"]):
			frappe.get_doc({"doctype": "Partnership Stage", **s}).insert(ignore_permissions=True)


def _seed_default_fund():
	if not frappe.db.exists("Fund", "General Support"):
		frappe.get_doc(
			{
				"doctype": "Fund",
				"fund_name": "General Support",
				"is_default": 1,
				"status": "Active",
			}
		).insert(ignore_permissions=True)
