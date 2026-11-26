# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Server side of the Summary Home desk page: sectioned dashboard for the frappe-ui island.

Sections, in order:
	module shortcuts, needs attention, at a glance, trends, website.
"""

import json

import frappe
from frappe.desk.doctype.dashboard_chart.dashboard_chart import get as get_chart_data
from frappe.desk.doctype.number_card.number_card import get_result as get_card_result

INTRO_VERSE = (
	'"And whatsoever ye do, do it heartily, as to the Lord, '
	'and not unto men" (Colossians 3:23)'
)

CARDS = [
	"Supporters",
	"Donations",
	"Active Trips",
	"Open Tasks",
	"Pending Applications",
	"Active Recurring Donations",
	"Pledges Committed",
	"Prayer Letters Sent",
	"Churches in Rolodex",
	"Missionary",
]

CHARTS = [
	"Donations by Fund",
	"Trips by Status",
	"Pledges by Status",
]

SHORTCUT_TONES = ("blue", "emerald", "indigo", "amber", "sky", "orange", "red")

SESSION = "<SESSION>"
# label, doctype, filters, lucide icon, colour tone
ATTENTION = [
	("My Assignments", "ToDo", {"allocated_to": SESSION, "status": "Open"}, "list-todo", "blue"),
	("Open Ministry Tasks", "Mit Correspondence Ministry Task", {"status": "Open"}, "clipboard-list", "orange"),
	(
		"Trip Applications to Review",
		"Mit Trip Application",
		{"status": ["in", ["Submitted", "Under Review"]]},
		"file-check",
		"amber",
	),
	(
		"Church Visits Coming Up",
		"Mit Deputation Church Visit",
		{"status": "Planned"},
		"calendar-days",
		"indigo",
	),
	("Pledges Promised", "Mit Finances Pledge", {"status": "Promised"}, "handshake", "emerald"),
]


@frappe.whitelist(methods=["GET"])
def get_dashboard() -> dict:
	"""The Summary Home dashboard, every section at once: verse, shortcuts, needs attention, at a glance,
	trends, and website. Reads only."""
	return {
		"verse": INTRO_VERSE,
		"shortcuts": get_shortcuts(),
		"attention": get_attention(),
		"cards": [card_payload(name) for name in CARDS if frappe.db.exists("Number Card", name)],
		"charts": [chart_payload(name) for name in CHARTS if frappe.db.exists("Dashboard Chart", name)],
		"website": get_website(),
	}


def get_shortcuts() -> list[dict]:
	"""One shortcut per visible dock entry (other than Overview itself), so the home
	reaches every module in one click. Tones cycle for visual variety."""
	if not frappe.db.exists("Dock", "missionsit"):
		return []
	dock = frappe.get_doc("Dock", "missionsit")
	tiles = []
	for item in dock.items:
		if item.link_type != "Sidebar" or item.hidden:
			continue
		if item.link_to == "Overview":
			continue
		tone = SHORTCUT_TONES[len(tiles) % len(SHORTCUT_TONES)]
		tiles.append(
			{
				"title": item.title,
				"sidebar": item.link_to,
				"icon": item.icon or "square",
				"tone": tone,
			}
		)
	return tiles


def get_attention() -> list[dict]:
	"""Open work items the reader can act on: assignments, tasks, applications, visits, pledges, recurring gifts."""
	user = frappe.session.user
	items = []
	for label, doctype, filters, icon, tone in ATTENTION:
		if not frappe.db.exists("DocType", doctype):
			continue
		filled = _fill_session(filters, user)
		try:
			count = frappe.db.count(doctype, filled)
		except Exception:
			frappe.log_error(title=f"Summary Home attention {doctype}")
			count = 0
		items.append(
			{
				"label": label,
				"doctype": doctype,
				"count": count,
				"icon": icon,
				"tone": tone,
				"filters": filled,
			}
		)
	return items


def get_website() -> dict:
	"""Rough state of the public front: donation pages, campaigns and missionary profiles."""
	return {
		"donation_pages": _safe_count("Mit Finances Donation Page"),
		"campaigns": _safe_count("Mit Website Campaign"),
		"missionary_profiles": _safe_count("Mit Website Missionary Profile Page"),
	}


def card_payload(name: str) -> dict:
	"""*name*'s label, value, and document type, for a card in the island."""
	doc = frappe.get_doc("Number Card", name)
	value = get_card_result(doc, doc.filters_json or [])
	return {
		"name": doc.name,
		"label": doc.label or doc.name,
		"value": value,
		"function": doc.function,
		"document_type": doc.document_type,
	}


def chart_payload(name: str) -> dict:
	"""*name*'s labels and datasets, for rendering with frappe.Chart in the island."""
	doc = frappe.get_doc("Dashboard Chart", name)
	try:
		# Frappe's cache_source wrapper drops chart_name on no_cache calls,
		# so pass a serialized doc that it can parse without re-fetching.
		result = get_chart_data(chart=json.dumps(doc.as_dict(convert_dates_to_str=True)), no_cache=1) or {}
	except Exception:
		frappe.log_error(title=f"Summary Home chart {name}")
		result = {}
	return {
		"name": doc.name,
		"label": doc.name,
		"type": doc.type,
		"document_type": doc.document_type,
		"labels": result.get("labels", []),
		"datasets": result.get("datasets") or [],
	}


def _fill_session(filters: dict, user: str) -> dict:
	return {k: (user if v == SESSION else v) for k, v in filters.items()}


def _safe_count(doctype: str) -> int:
	if not frappe.db.exists("DocType", doctype):
		return 0
	try:
		return frappe.db.count(doctype)
	except Exception:
		return 0
