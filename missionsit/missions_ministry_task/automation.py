# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Scheduled Ministry Task creators for birthdays, anniversaries and lapsed donors."""

import frappe
from frappe.utils import add_days, getdate, today


LAPSED_WINDOW_DAYS = 90
BIRTHDAY_LEAD_DAYS = 7
ANNIVERSARY_LEAD_DAYS = 7


def create_birthday_tasks():
	"""Create a Birthday Ministry Task for each supporter whose birthday is in BIRTHDAY_LEAD_DAYS."""
	target = _month_day(add_days(today(), BIRTHDAY_LEAD_DAYS))
	supporters = _supporters_matching_month_day("birthday", target)
	for supporter in supporters:
		_ensure_task(
			supporter=supporter,
			tag="Birthday",
			title=frappe._("Birthday: {0}").format(supporter.full_name),
			due_date=add_days(today(), BIRTHDAY_LEAD_DAYS),
		)


def create_anniversary_tasks():
	"""Create an Anniversary Ministry Task for each supporter with an anniversary in ANNIVERSARY_LEAD_DAYS."""
	target = _month_day(add_days(today(), ANNIVERSARY_LEAD_DAYS))
	supporters = _supporters_matching_month_day("anniversary", target)
	for supporter in supporters:
		_ensure_task(
			supporter=supporter,
			tag="Other",
			title=frappe._("Anniversary: {0}").format(supporter.full_name),
			due_date=add_days(today(), ANNIVERSARY_LEAD_DAYS),
		)


def create_lapsed_donor_tasks():
	"""Create a Lapsed Ministry Task for supporters with no donation in the last 90 days."""
	cutoff = add_days(today(), -LAPSED_WINDOW_DAYS)
	rows = frappe.db.sql(
		"""
		SELECT s.name, s.full_name, s.missionary
		FROM `tabSupporter` s
		WHERE s.status = 'Active'
		  AND NOT EXISTS (
		    SELECT 1 FROM `tabDonation` d
		    WHERE d.supporter = s.name
		      AND d.donation_date >= %(cutoff)s
		  )
		  AND EXISTS (
		    SELECT 1 FROM `tabDonation` d2 WHERE d2.supporter = s.name
		  )
		""",
		{"cutoff": cutoff},
		as_dict=True,
	)
	for row in rows:
		_ensure_task(
			supporter=frappe._dict(name=row.name, full_name=row.full_name, missionary=row.missionary),
			tag="Lapsed",
			title=frappe._("Reconnect with lapsed partner: {0}").format(row.full_name),
			due_date=add_days(today(), 3),
			priority="High",
		)


def _supporters_matching_month_day(field: str, month_day: str) -> list[frappe._dict]:
	"""Return supporters whose *field* (MM-DD) matches *month_day*, with missionary."""
	rows = frappe.db.sql(
		f"""
		SELECT name, full_name, missionary
		FROM `tabSupporter`
		WHERE {field} IS NOT NULL
		  AND DATE_FORMAT({field}, '%%m-%%d') = %(target)s
		  AND status = 'Active'
		""",
		{"target": month_day},
		as_dict=True,
	)
	return rows


def _ensure_task(*, supporter, tag: str, title: str, due_date, priority: str = "Medium"):
	"""Insert a Ministry Task when none exists for this supporter, tag and due_date."""
	existing = frappe.db.exists(
		"Ministry Task",
		{
			"supporter": supporter.name,
			"tag": tag,
			"due_date": due_date,
		},
	)
	if existing:
		return
	frappe.get_doc(
		{
			"doctype": "Ministry Task",
			"title": title,
			"task_type": "Other" if tag != "Birthday" else "Call",
			"tag": tag,
			"supporter": supporter.name,
			"missionary": supporter.missionary,
			"due_date": due_date,
			"status": "Open",
			"priority": priority,
		}
	).insert(ignore_permissions=True)


def _month_day(date) -> str:
	"""Format a date as MM-DD."""
	d = getdate(date)
	return f"{d.month:02d}-{d.day:02d}"


