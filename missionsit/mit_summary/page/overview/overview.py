# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Server side of the Overview desk page, read by its frappe-ui island.

Sections, in order: support level, work waiting on the reader, the support ledger (number
cards and website counts), what is coming up in the next fortnight, trends, module links.
"""

import frappe
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


COMING_UP_DAYS = 14
LATER_DAYS = 180
RECEIPT_WINDOW_DAYS = 90
FOLLOW_UP_WINDOW_DAYS = 14

# How many of each frequency fall in a month, for turning commitments into a monthly figure.
# A one-time pledge is not ongoing support, so it does not count.
PER_MONTH = {"Monthly": 1, "Quarterly": 1 / 3, "Annual": 1 / 12}


def attention_rows(user: str) -> list[tuple]:
	"""Work waiting on the reader: label, doctype, filters, lucide icon.

	Only things someone has to act on. Status counts, such as active recurring gifts, belong
	in the ledger. First gifts are not listed: recording one creates a Thank You task, which
	the task rows already count.
	"""
	today = frappe.utils.today()
	add = frappe.utils.add_days
	return [
		("My assignments", "ToDo", {"allocated_to": user, "status": "Open"}, "list-todo"),
		(
			"Overdue tasks",
			"Mit Correspondence Ministry Task",
			{"status": "Open", "due_date": ["<", today]},
			"alarm-clock",
		),
		(
			"Tasks due this week",
			"Mit Correspondence Ministry Task",
			{"status": "Open", "due_date": ["between", [today, add(today, 6)]]},
			"clipboard-list",
		),
		(
			"Follow-ups due",
			"Mit Correspondence Log",
			{"follow_up_date": ["between", [add(today, -FOLLOW_UP_WINDOW_DAYS), today]]},
			"message-circle-reply",
		),
		(
			"Receipts to send",
			"Mit Finances Donation",
			{"receipt_sent": 0, "donation_date": [">=", add(today, -RECEIPT_WINDOW_DAYS)]},
			"receipt",
		),
		(
			"Trip applications to review",
			"Mit Trip Application",
			{"status": ["in", ["Submitted", "Under Review"]]},
			"file-check",
		),
		(
			"Church submissions to review",
			"Mit Directory Church Submission",
			{"status": "Pending Review"},
			"building-2",
		),
		("Directory access requests", "Mit Directory Access Request", {"status": "Pending"}, "key-round"),
		("Prayer letters in draft", "Mit Correspondence Prayer Letter", {"status": "Draft"}, "mail"),
		("Prayer updates in draft", "Mit Prayer Update", {"status": "Draft"}, "hand-heart"),
	]


@frappe.whitelist(methods=["GET"])
def get_dashboard() -> dict:
	"""The Overview dashboard, every section at once. Reads only, and counts only what the reader
	is allowed to see."""
	coming_up = get_coming_up()
	return {
		"verse": INTRO_VERSE,
		"support": get_support(),
		"coming_up": coming_up,
		# Only looked for when the fortnight is empty, so the page still says what is next.
		"coming_later": [] if coming_up else get_coming_up(days=LATER_DAYS, limit=3),
		"shortcuts": get_shortcuts(),
		"attention": get_attention(),
		"cards": [card_payload(name) for name in CARDS if frappe.db.exists("Number Card", name)],
		"trends": TRENDS_MENU,
		"website": get_website(),
	}


def get_shortcuts() -> list[dict]:
	"""One shortcut per visible dock entry (other than Overview itself), so the home
	reaches every module in one click."""
	if not frappe.db.exists("Dock", "missionsit"):
		return []
	dock = frappe.get_doc("Dock", "missionsit")
	tiles = []
	for item in dock.items:
		if item.link_type != "Sidebar" or item.hidden:
			continue
		if item.link_to == "Overview":
			continue
		tiles.append(
			{
				"title": item.title,
				"sidebar": item.link_to,
				"icon": item.icon or "square",
			}
		)
	return tiles


def get_attention() -> list[dict]:
	"""Work waiting on the reader, each with its count and the filters that open it as a list."""
	items = []
	for label, doctype, filters, icon in attention_rows(frappe.session.user):
		if not frappe.db.exists("DocType", doctype):
			continue
		items.append(
			{
				"label": label,
				"doctype": doctype,
				"count": _count(doctype, filters, title=f"Overview attention {doctype}"),
				"icon": icon,
				"filters": filters,
			}
		)
	return items


def get_support() -> dict | None:
	"""Monthly support committed against the target, for the missionaries the reader can see.

	A Missionary user sees their own record. An Organization Admin sees the organization's
	missionaries, added together. Committed support is pledges that are giving plus active
	recurring gifts, each turned into a monthly amount. Promised pledges are shown apart, since
	they are not coming in yet.

	A pledge and a recurring gift for the same commitment would both count. They are separate
	records with no link between them, so there is nothing to match them on.
	"""
	missionaries = frappe.get_list(
		"Mit People Missionary",
		fields=["name", "missionary_name", "full_support_target", "currency"],
		limit_page_length=0,
	)
	targeted = [m for m in missionaries if m.full_support_target]
	if not targeted:
		return None

	names = [m.name for m in targeted]
	currencies = {m.currency for m in targeted if m.currency}

	def monthly(doctype: str, status: str) -> float:
		rows = frappe.get_list(
			doctype,
			filters={"missionary": ["in", names], "status": status},
			fields=["amount", "frequency"],
			limit_page_length=0,
		)
		return sum((r.amount or 0) * PER_MONTH.get(r.frequency, 0) for r in rows)

	committed = monthly("Mit Finances Pledge", "Giving") + monthly("Mit Finances Recurring Donation", "Active")
	promised = monthly("Mit Finances Pledge", "Promised")
	target = sum(m.full_support_target for m in targeted)

	return {
		"who": targeted[0].missionary_name if len(targeted) == 1 else None,
		"missionaries": len(targeted),
		"target": target,
		"committed": committed,
		"promised": promised,
		"percent": round(committed / target * 100) if target else 0,
		# Amounts in different currencies cannot be added, so only name one when they agree.
		"currency": currencies.pop() if len(currencies) == 1 else None,
	}


def get_coming_up(days: int = COMING_UP_DAYS, limit: int = 12) -> list[dict]:
	"""Dated things in the next *days* days: church visits, trips, furlough, scheduled emails, and
	supporters' birthdays and anniversaries. Soonest first, at most *limit*."""
	today = frappe.utils.getdate()
	until = frappe.utils.add_days(today, days - 1)
	window = ["between", [today, until]]
	items = []

	def add(date, kind, title, doctype, name, icon):
		items.append(
			{
				"date": str(date),
				"kind": kind,
				"title": title,
				"doctype": doctype,
				"name": name,
				"icon": icon,
			}
		)

	visits = _list(
		"Mit Deputation Church Visit",
		{"status": "Planned", "visit_date": window},
		["name", "visit_date", "church"],
	)
	churches = _titles("Mit Directory Church", "church_name", [v.church for v in visits])
	for v in visits:
		add(v.visit_date, "Church visit", churches.get(v.church, v.church), v.doctype, v.name, "church")

	for t in _list(
		"Mit Trip", {"status": ["not in", ["Cancelled", "Completed"]], "start_date": window}, ["name", "start_date"]
	):
		add(t.start_date, "Trip starts", t.name, t.doctype, t.name, "plane")

	furloughs = _list(
		"Mit Furlough", {"status": "Planned", "start_date": window}, ["name", "start_date", "missionary"]
	)
	names = _titles("Mit People Missionary", "missionary_name", [f.missionary for f in furloughs])
	for f in furloughs:
		add(f.start_date, "Furlough starts", names.get(f.missionary, f.missionary), f.doctype, f.name, "house")

	for c in _list(
		"Mit Correspondence Email Campaign",
		{"status": "Scheduled", "scheduled_date": window},
		["name", "scheduled_date"],
	):
		add(c.scheduled_date, "Email goes out", c.name, c.doctype, c.name, "send")

	for s in _list(
		"Mit People Supporter",
		{"status": "Active"},
		["name", "full_name", "birthday", "anniversary"],
		or_filters={"birthday": ["is", "set"], "anniversary": ["is", "set"]},
	):
		for field, kind, icon in (("birthday", "Birthday", "cake"), ("anniversary", "Anniversary", "heart")):
			date = _next_occurrence(s.get(field), today)
			if date and date <= until:
				add(date, kind, s.full_name or s.name, s.doctype, s.name, icon)

	items.sort(key=lambda i: (i["date"], i["kind"], i["title"]))
	return items[:limit]


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


# The trends the page can draw: subject, then the ways to slice it. The first view of the first
# subject is what the page opens on.
TRENDS_MENU = [
	{
		"key": "donations",
		"label": "Donations",
		"views": [
			{"key": "month", "label": "Given each month", "total": "given in the last 12 months"},
			{"key": "fund", "label": "Given by fund", "total": "given in the last 12 months"},
			{"key": "method", "label": "Given by payment method", "total": "given in the last 12 months"},
			{"key": "givers", "label": "Givers each month", "total": "people gave in the last 12 months"},
		],
	},
	{
		"key": "pledges",
		"label": "Pledges",
		"views": [
			{"key": "monthly", "label": "Monthly value by status", "total": "a month across all pledges"},
			{"key": "status", "label": "Pledges by status", "total": "pledges"},
			{"key": "frequency", "label": "Pledges by frequency", "total": "pledges"},
		],
	},
	{
		"key": "trips",
		"label": "Trips",
		"views": [
			{"key": "status", "label": "Trips by status", "total": "trips"},
			{"key": "month", "label": "Trips starting each month", "total": "trips starting in these 12 months"},
			{"key": "applications", "label": "Applications by status", "total": "trip applications"},
		],
	},
]

TREND_MONTHS = 12


@frappe.whitelist(methods=["GET"])
def get_trend(subject: str, view: str) -> dict:
	"""One trend for the chart panel: labels, one series of values, how to draw it, and whether
	the values are money. Counts only what the reader is allowed to see."""
	builders = {
		("donations", "month"): _donations_by_month,
		("donations", "fund"): lambda: _group(
			"Mit Finances Donation", "fund", "amount", money=True, filters=_last_year("donation_date")
		),
		("donations", "method"): lambda: _group(
			"Mit Finances Donation", "payment_method", "amount", money=True, filters=_last_year("donation_date")
		),
		("donations", "givers"): _givers_by_month,
		("pledges", "monthly"): _pledges_monthly_by_status,
		("pledges", "status"): lambda: _group("Mit Finances Pledge", "status"),
		("pledges", "frequency"): lambda: _group("Mit Finances Pledge", "frequency"),
		("trips", "status"): lambda: _group("Mit Trip", "status"),
		("trips", "month"): _trips_by_month,
		("trips", "applications"): lambda: _group("Mit Trip Application", "status"),
	}
	build = builders.get((subject, view))
	if not build:
		frappe.throw(frappe._("There is no {0} trend called {1}.").format(subject, view))
	return build()


def _trend(labels, values, kind="bar", money=False, currency=None, total=None) -> dict:
	return {
		"labels": labels,
		"values": values,
		"type": kind,
		"money": money,
		"currency": currency,
		"total": sum(values) if total is None else total,
	}


def _group(
	doctype: str, field: str, amount: str | None = None, money: bool = False, filters: dict | None = None
) -> dict:
	"""Count (or sum *amount*) of *doctype* grouped by *field*, largest first."""
	fields = ["name", field] + ([amount] if amount else []) + (["currency"] if money else [])
	totals = {}
	currencies = set()
	for row in _list(doctype, filters or {}, fields):
		key = row.get(field) or frappe._("Not set")
		totals[key] = totals.get(key, 0) + ((row.get(amount) or 0) if amount else 1)
		if money and row.get("currency"):
			currencies.add(row.currency)
	ordered = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
	return _trend(
		[k for k, _ in ordered],
		[round(v, 2) for _, v in ordered],
		money=money,
		currency=currencies.pop() if len(currencies) == 1 else None,
	)


def _month_keys(start, months: int) -> list:
	"""The first day of each of *months* months from *start*."""
	keys = []
	date = start.replace(day=1)
	for _ in range(months):
		keys.append(date)
		date = frappe.utils.add_months(date, 1)
	return keys


def _month_labels(months: list) -> list[str]:
	"""Short month names, with the year on the first month and on each January."""
	return [m.strftime("%b %Y") if i == 0 or m.month == 1 else m.strftime("%b") for i, m in enumerate(months)]


def _last_year(field: str) -> dict:
	return {field: [">=", _last_months()[0]]}


def _last_months() -> list:
	today = frappe.utils.getdate()
	return _month_keys(frappe.utils.add_months(today, -(TREND_MONTHS - 1)), TREND_MONTHS)


def _by_month(rows, date_field: str, months: list, value=lambda row: 1) -> list:
	index = {(m.year, m.month): i for i, m in enumerate(months)}
	values = [0] * len(months)
	for row in rows:
		date = row.get(date_field)
		if not date:
			continue
		date = frappe.utils.getdate(date)
		i = index.get((date.year, date.month))
		if i is not None:
			values[i] += value(row)
	return values


def _donations_by_month() -> dict:
	months = _last_months()
	rows = _list(
		"Mit Finances Donation",
		{"donation_date": [">=", months[0]]},
		["name", "donation_date", "amount", "currency"],
	)
	values = [round(v, 2) for v in _by_month(rows, "donation_date", months, lambda r: r.amount or 0)]
	currencies = {r.currency for r in rows if r.currency}
	return _trend(
		_month_labels(months),
		values,
		kind="line",
		money=True,
		currency=currencies.pop() if len(currencies) == 1 else None,
	)


def _givers_by_month() -> dict:
	"""Distinct supporters who gave in each of the last twelve months."""
	months = _last_months()
	rows = _list(
		"Mit Finances Donation", {"donation_date": [">=", months[0]]}, ["name", "donation_date", "supporter"]
	)
	seen = [set() for _ in months]
	index = {(m.year, m.month): i for i, m in enumerate(months)}
	for row in rows:
		date = frappe.utils.getdate(row.donation_date) if row.donation_date else None
		i = index.get((date.year, date.month)) if date else None
		if i is not None and row.supporter:
			seen[i].add(row.supporter)
	givers = {s for month in seen for s in month}
	return _trend(_month_labels(months), [len(s) for s in seen], total=len(givers))


def _pledges_monthly_by_status() -> dict:
	"""What each pledge status is worth a month, so promised and paused support can be weighed
	against what is giving."""
	totals = {}
	currencies = set()
	for row in _list("Mit Finances Pledge", {}, ["name", "status", "amount", "frequency", "currency"]):
		monthly = (row.amount or 0) * PER_MONTH.get(row.frequency, 0)
		if not monthly:
			continue
		totals[row.status] = totals.get(row.status, 0) + monthly
		if row.currency:
			currencies.add(row.currency)
	order = ["Giving", "Promised", "Paused", "Lapsed", "Ended"]
	labels = [s for s in order if s in totals] + [s for s in totals if s not in order]
	return _trend(
		labels,
		[round(totals[s], 2) for s in labels],
		money=True,
		currency=currencies.pop() if len(currencies) == 1 else None,
	)


def _trips_by_month() -> dict:
	"""Trips starting in each month, from six months back to five ahead."""
	today = frappe.utils.getdate()
	months = _month_keys(frappe.utils.add_months(today, -6), TREND_MONTHS)
	rows = _list(
		"Mit Trip",
		{"start_date": ["between", [months[0], frappe.utils.add_months(months[-1], 1)]], "status": ["!=", "Cancelled"]},
		["name", "start_date"],
	)
	return _trend(_month_labels(months), _by_month(rows, "start_date", months))


def _count(doctype: str, filters: dict, title: str) -> int:
	"""How many *doctype* records match *filters* that the reader may see."""
	try:
		return len(frappe.get_list(doctype, filters=filters, pluck="name", limit_page_length=0))
	except Exception:
		frappe.log_error(title=title)
		return 0


def _list(doctype: str, filters: dict, fields: list[str], or_filters: dict | None = None) -> list:
	"""The matching records the reader may see, each tagged with its doctype. Empty when the
	doctype is missing or the read fails, so one broken source does not blank the page."""
	if not frappe.db.exists("DocType", doctype):
		return []
	try:
		rows = frappe.get_list(
			doctype, filters=filters, or_filters=or_filters, fields=fields, limit_page_length=0
		)
	except Exception:
		frappe.log_error(title=f"Overview coming up {doctype}")
		return []
	for row in rows:
		row.doctype = doctype
	return rows


def _titles(doctype: str, field: str, names: list[str]) -> dict[str, str]:
	"""*field* for each of *names*, read in one query."""
	names = [n for n in set(names) if n]
	if not names:
		return {}
	rows = frappe.get_all(doctype, filters={"name": ["in", names]}, fields=["name", field])
	return {r.name: r.get(field) for r in rows if r.get(field)}


def _next_occurrence(date, today):
	"""The next time the day and month of *date* come round, from *today* on. A 29 February
	falls on 28 February in other years."""
	if not date:
		return None
	date = frappe.utils.getdate(date)
	for year in (today.year, today.year + 1):
		try:
			candidate = date.replace(year=year)
		except ValueError:
			candidate = date.replace(year=year, day=28)
		if candidate >= today:
			return candidate
	return None


def _safe_count(doctype: str) -> int:
	if not frappe.db.exists("DocType", doctype):
		return 0
	return _count(doctype, {}, title=f"Overview website {doctype}")
