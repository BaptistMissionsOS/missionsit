# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Server side of the Web App desk home, read by its frappe-ui island.

It answers three questions for whoever runs the public site: is it switched on, what is
published on it, and what is missing before it looks complete.
"""

import frappe
from frappe import _

from missionsit.api.web import _active_campaigns, _donation_pages

PORTAL = "Mit Website Portal"
SWITCHES = {
	"enable_signups": "Member signups",
	"enable_donations": "Online giving",
	"enable_trip_applications": "Trip applications",
}


@frappe.whitelist(methods=["GET"])
def get_home() -> dict:
	portal = frappe.get_cached_doc(PORTAL)
	return {
		"url": "/missions",
		"title": portal.portal_title or _("Missions"),
		"can_edit": frappe.has_permission(PORTAL, "write"),
		"switches": [
			{"field": field, "label": _(label), "on": bool(portal.get(field))} for field, label in SWITCHES.items()
		],
		"published": _published_counts(),
		"checklist": _checklist(),
		"pages": _donation_pages(limit=4),
		"campaigns": _active_campaigns(limit=4),
		"applications": frappe.get_list(
			"Mit Trip Application",
			fields=["name", "applicant_name", "trip", "status", "application_date"],
			order_by="application_date desc, creation desc",
			limit_page_length=5,
		),
		"gifts": frappe.get_list(
			"Mit Finances Donation",
			filters={"donation_page": ["is", "set"]},
			fields=["name", "supporter", "amount", "currency", "donation_date", "donation_page"],
			order_by="donation_date desc, creation desc",
			limit_page_length=5,
		),
	}


@frappe.whitelist(methods=["POST"])
def set_switch(field: str, on: int | str | bool) -> dict:
	"""Turn one of the portal's switches on or off, as the reader."""
	if field not in SWITCHES:
		frappe.throw(_("{0} is not a web app switch.").format(field))
	portal = frappe.get_doc(PORTAL)
	portal.check_permission("write")
	portal.set(field, 1 if frappe.utils.cint(on) else 0)
	portal.save()
	return {"field": field, "on": bool(portal.get(field))}


def _count(doctype: str, filters: dict | None = None) -> int:
	return len(frappe.get_list(doctype, filters=filters or {}, pluck="name", limit_page_length=0))


def _published_counts() -> list[dict]:
	today = frappe.utils.today()
	return [
		{
			"label": _("Missionary profiles"),
			"value": _count("Mit Website Missionary Profile Page", {"is_published": 1}),
			"of": _count("Mit People Missionary"),
			"doctype": "Mit Website Missionary Profile Page",
		},
		{
			"label": _("Gift pages"),
			"value": _count("Mit Finances Donation Page", {"is_active": 1, "slug": ["is", "set"]}),
			"doctype": "Mit Finances Donation Page",
		},
		{
			"label": _("Campaigns"),
			"value": _count("Mit Website Campaign", {"status": "Active"}),
			"doctype": "Mit Website Campaign",
		},
		{
			"label": _("Upcoming trips"),
			"value": _count(
				"Mit Trip", {"status": ["in", ["Planning", "Open", "Full"]], "start_date": [">=", today]}
			),
			"doctype": "Mit Trip",
		},
	]


def _checklist() -> list[dict]:
	"""Gaps that make the public site look unfinished, each with the list that fixes it."""
	profiled = set(
		frappe.get_list(
			"Mit Website Missionary Profile Page",
			filters={"is_published": 1},
			pluck="missionary",
			limit_page_length=0,
		)
	)
	without_profile = [
		m for m in frappe.get_list("Mit People Missionary", pluck="name", limit_page_length=0) if m not in profiled
	]
	items = [
		{
			"label": _("Missionaries without a published profile"),
			"count": len(without_profile),
			"doctype": "Mit People Missionary",
			"filters": {"name": ["in", without_profile]} if without_profile else {},
		},
		{
			"label": _("Published profiles without a photo"),
			"count": _count("Mit Website Missionary Profile Page", {"is_published": 1, "profile_image": ["is", "not set"]}),
			"doctype": "Mit Website Missionary Profile Page",
			"filters": {"is_published": 1, "profile_image": ["is", "not set"]},
		},
		{
			"label": _("Active gift pages without a link"),
			"count": _count("Mit Finances Donation Page", {"is_active": 1, "slug": ["is", "not set"]}),
			"doctype": "Mit Finances Donation Page",
			"filters": {"is_active": 1, "slug": ["is", "not set"]},
		},
		{
			"label": _("Open trips without a description"),
			"count": _count("Mit Trip", {"status": "Open", "description": ["is", "not set"]}),
			"doctype": "Mit Trip",
			"filters": {"status": "Open", "description": ["is", "not set"]},
		},
	]
	return items
