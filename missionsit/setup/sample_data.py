# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Idempotent KJV-themed sample data for Overview Home demos.

Run from pilot: ``pilot -b church-dev frappe --site missionsit.localhost \\
execute missionsit.setup.sample_data.load_sample_data``.
"""

import frappe
from frappe.utils import add_days, add_months, today


_ORG = {"organization_name": "Antioch Sending Society", "organization_type": "Mission Board"}

_CHURCHES = [
	{"church_name": "First Baptist Church of Antioch", "pastor_name": "Barnabas", "country": "Syria", "city": "Antioch"},
	{"church_name": "Jerusalem Baptist Church",        "pastor_name": "James",    "country": "Israel", "city": "Jerusalem"},
	{"church_name": "Ephesus Baptist Church",          "pastor_name": "John",     "country": "Greece", "city": "Ephesus"},
	{"church_name": "Berea Baptist Church",            "pastor_name": "Sopater",  "country": "Greece", "city": "Berea"},
	{"church_name": "Philippi Baptist Church",         "pastor_name": "Lydia",    "country": "Greece", "city": "Philippi"},
	{"church_name": "Corinth Baptist Church",          "pastor_name": "Apollos",  "country": "Greece", "city": "Corinth"},
]

_MISSIONARIES = [
	{"missionary_name": "Paul of Tarsus",    "status": "On Field",        "field_country": "Greece",    "sending_church": "First Baptist Church of Antioch", "full_support_target": 5500},
	{"missionary_name": "Timothy Judean",    "status": "On Field",        "field_country": "Greece",    "sending_church": "Ephesus Baptist Church",          "full_support_target": 4200},
	{"missionary_name": "Barnabas Levi",     "status": "Home Assignment", "field_country": "Cyprus",    "sending_church": "First Baptist Church of Antioch", "full_support_target": 4800},
	{"missionary_name": "Silas Antiochan",   "status": "Deputation",      "field_country": "Macedonia", "sending_church": "First Baptist Church of Antioch", "full_support_target": 5000},
	{"missionary_name": "Philip Evangelist", "status": "On Field",        "field_country": "Ethiopia",  "sending_church": "Jerusalem Baptist Church",        "full_support_target": 4500},
]

_SUPPORTERS = [
	("Lydia of Thyatira",    "Lydia",       "Thyatira",    "Paul of Tarsus",     "Partner",       100),
	("Aquila ben Pontus",    "Aquila",      "ben Pontus",  "Paul of Tarsus",     "Partner",       150),
	("Phoebe of Cenchrea",   "Phoebe",      "of Cenchrea", "Timothy Judean",     "Partner",        75),
	("Onesiphorus Ephesian", "Onesiphorus", "Ephesian",    "Timothy Judean",     "Presentation",   50),
	("Gaius of Macedonia",   "Gaius",       "of Macedonia","Barnabas Levi",      "Partner",       125),
	("Jason of Thessalonica","Jason",       "of Thessalonica","Barnabas Levi",   "Appointment",   None),
	("Crispus of Corinth",   "Crispus",     "of Corinth",  "Silas Antiochan",    "Partner",        80),
	("Stephanas of Achaia",  "Stephanas",   "of Achaia",   "Silas Antiochan",    "Contact",       None),
	("Cornelius Centurion",  "Cornelius",   "Centurion",   "Philip Evangelist",  "Partner",       200),
	("Mnason of Cyprus",     "Mnason",      "of Cyprus",   "Philip Evangelist",  "Presentation",   60),
]

_TRIPS = [
	{"trip_name": "Macedonia Call 2026",  "status": "Open",      "destination": "Thessalonica", "missionary": "Silas Antiochan",   "total_goal": 12000, "start": 60, "end": 74},
	{"trip_name": "Ephesus Outreach",     "status": "Planning",  "destination": "Ephesus",      "missionary": "Timothy Judean",    "total_goal":  8500, "start": 90, "end": 97},
	{"trip_name": "Cyprus Return Journey","status": "Completed", "destination": "Salamis",      "missionary": "Barnabas Levi",     "total_goal":  6000, "start": -40, "end": -30},
]

_APPLICANTS = [
	("Luke the Physician",    "luke@example.com",       "Macedonia Call 2026",  "Submitted"),
	("Mark Johanan",          "mark@example.com",       "Macedonia Call 2026",  "Accepted"),
	("Tychicus of Asia",      "tychicus@example.com",   "Macedonia Call 2026",  "Under Review"),
	("Demas Thessalonian",    "demas@example.com",      "Ephesus Outreach",     "Submitted"),
	("Trophimus Ephesian",    "trophimus@example.com",  "Ephesus Outreach",     "Waitlist"),
	("Epaphras of Colossae",  "epaphras@example.com",   "Ephesus Outreach",     "Accepted"),
]

_PRAYER_LETTERS = [
	("Greetings from Greece",       "Paul of Tarsus",    -14, "Sent"),
	("Sailing for Macedonia",       "Paul of Tarsus",     -3, "Draft"),
	("Timothy's Autumn Update",     "Timothy Judean",    -21, "Sent"),
	("From the Hills of Ephesus",   "Timothy Judean",     -2, "Draft"),
	("Furlough Progress",           "Barnabas Levi",     -30, "Sent"),
	("Cyprus in Our Hearts",        "Barnabas Levi",     -10, "Sent"),
	("Deputation Doors Opening",    "Silas Antiochan",   -45, "Sent"),
	("From Ethiopia with Joy",      "Philip Evangelist", -18, "Sent"),
]

_TASKS = [
	# (title, task_type, tag, supporter, missionary, status, priority, due_offset)
	("Thank You note to Lydia",  "Thank You",   "Thank",                  "Lydia of Thyatira",     "Paul of Tarsus",    "Open",      "High",   -1),
	("Call Phoebe about Pledge", "Call",        "Follow-up",              "Phoebe of Cenchrea",    "Timothy Judean",    "Open",      "Medium",  3),
	("Challenge Onesiphorus",    "Appointment", "Partnership Challenge",  "Onesiphorus Ephesian",  "Timothy Judean",    "Open",      "Medium",  7),
	("Birthday Note to Gaius",   "Letter",      "Birthday",               "Gaius of Macedonia",    "Barnabas Levi",     "Open",      "Low",     5),
	("Lapsed Follow-up Jason",   "Call",        "Lapsed",                 "Jason of Thessalonica", "Barnabas Levi",     "Open",      "High",   -2),
	("Email Stephanas",          "Email",       "Follow-up",              "Stephanas of Achaia",   "Silas Antiochan",   "Open",      "Medium",  4),
	("Visit Cornelius",          "Visit",       "Follow-up",              "Cornelius Centurion",   "Philip Evangelist", "Open",      "Low",    10),
	("Spring Letter Mailing",    "Letter",      "Other",                  None,                    "Paul of Tarsus",    "Open",      "Medium", 14),
	("Thank Aquila",             "Thank You",   "Thank",                  "Aquila ben Pontus",     "Paul of Tarsus",    "Completed", "High",  -10),
	("Review Mnason Pledge",     "Call",        "Follow-up",              "Mnason of Cyprus",      "Philip Evangelist", "Completed", "Medium", -5),
]

# Dated relative to today so Coming up always has something in each range.
# (supporter, birthday offset in days or None, anniversary offset in days or None)
_OCCASIONS = [
	("Lydia of Thyatira",    2,    None),
	("Gaius of Macedonia",   5,    None),  # matches the "Birthday Note to Gaius" task, so it shows as planned
	("Aquila ben Pontus",    None, 6),
	("Phoebe of Cenchrea",   11,   None),
	("Cornelius Centurion",  None, 19),
	("Crispus of Corinth",   26,   None),
	("Mnason of Cyprus",     None, 48),
]

# (church_name, missionary, day offset, visit_type, status)
_CHURCH_VISITS = [
	("Berea Baptist Church",           "Silas Antiochan", 1,  "Sunday Service",      "Planned"),
	("Philippi Baptist Church",        "Barnabas Levi",   4,  "Furlough Report",     "Planned"),
	("Corinth Baptist Church",         "Silas Antiochan", 12, "Mission Committee",   "Planned"),
	("Ephesus Baptist Church",         "Timothy Judean",  33, "Presentation",        "Planned"),
	("Jerusalem Baptist Church",       "Silas Antiochan", -8, "Meeting with Pastor", "Completed"),
]

# (title, missionary, scheduled day offset)
_EMAIL_CAMPAIGNS = [
	("Christmas Greetings from the Field", "Paul of Tarsus", 9),
]

# (missionary, start offset, end offset)
_FURLOUGHS = [
	("Paul of Tarsus", 52, 230),
]


def load_sample_data() -> None:
	"""Create the KJV-themed demo dataset. Safe to re-run."""
	org = _ensure_organization()
	_ensure_churches(org)
	_ensure_missionaries(org)
	_ensure_supporters(org)
	_ensure_pledges()
	_ensure_recurring_donations()
	_ensure_donations()
	_ensure_trips()
	_ensure_trip_applications()
	_ensure_prayer_letters()
	_ensure_tasks()
	_ensure_occasions()
	_ensure_church_visits()
	_ensure_email_campaigns()
	_ensure_furloughs()
	frappe.db.commit()


def _ensure_organization() -> str:
	if not frappe.db.exists("Mit People Organization", _ORG["organization_name"]):
		frappe.get_doc({"doctype": "Mit People Organization", **_ORG}).insert(ignore_permissions=True)
	return _ORG["organization_name"]


def _ensure_churches(org: str) -> None:
	for c in _CHURCHES:
		if frappe.db.exists("Mit Directory Church", {"church_name": c["church_name"]}):
			continue
		frappe.get_doc({"doctype": "Mit Directory Church", "organization": org, **c}).insert(ignore_permissions=True)


def _ensure_missionaries(org: str) -> None:
	for m in _MISSIONARIES:
		if frappe.db.exists("Mit People Missionary", m["missionary_name"]):
			continue
		data = {**m, "sending_church": _church_name(m["sending_church"])}
		frappe.get_doc({"doctype": "Mit People Missionary", "organization": org, "support_model": "Deputation", **data}).insert(ignore_permissions=True)


def _church_name(church_name: str) -> str | None:
	"""Resolve a church_name to its CHURCH-##### record name."""
	return frappe.db.get_value("Mit Directory Church", {"church_name": church_name}, "name")


def _ensure_supporters(org: str) -> None:
	for full, first, last, missionary, stage, _amount in _SUPPORTERS:
		if frappe.db.exists("Mit People Supporter", full):
			continue
		frappe.get_doc(
			{
				"doctype": "Mit People Supporter",
				"full_name": full,
				"first_name": first,
				"last_name": last,
				"missionary": missionary,
				"partnership_stage": stage,
				"status": "Active",
				"organization": org,
			}
		).insert(ignore_permissions=True)


def _ensure_pledges() -> None:
	for full, _f, _l, missionary, _s, amount in _SUPPORTERS:
		if amount is None:
			continue
		if frappe.db.exists("Mit Finances Pledge", {"supporter": full, "missionary": missionary}):
			continue
		frappe.get_doc(
			{
				"doctype": "Mit Finances Pledge",
				"supporter": full,
				"missionary": missionary,
				"fund": "General Support",
				"amount": amount,
				"frequency": "Monthly",
				"status": "Giving",
				"start_date": add_months(today(), -6),
			}
		).insert(ignore_permissions=True)


def _ensure_recurring_donations() -> None:
	recurring_from = ("Lydia of Thyatira", "Aquila ben Pontus", "Cornelius Centurion")
	for full in recurring_from:
		row = next(r for r in _SUPPORTERS if r[0] == full)
		if frappe.db.exists("Mit Finances Recurring Donation", {"supporter": full}):
			continue
		frappe.get_doc(
			{
				"doctype": "Mit Finances Recurring Donation",
				"supporter": full,
				"missionary": row[3],
				"fund": "General Support",
				"amount": row[5],
				"frequency": "Monthly",
				"status": "Active",
				"start_date": add_months(today(), -6),
				"next_payment_date": add_days(today(), 7),
				"payment_method": "Stripe",
			}
		).insert(ignore_permissions=True)


def _ensure_donations() -> None:
	givers = [r for r in _SUPPORTERS if r[5] is not None]
	offsets = (-150, -120, -90, -60, -30, -5)
	for full, _f, _l, missionary, _s, amount in givers:
		for i, offset in enumerate(offsets[:3 if amount < 100 else 4]):
			ref = f"{full}-{offset}"
			if frappe.db.exists("Mit Finances Donation", {"reference": ref}):
				continue
			frappe.get_doc(
				{
					"doctype": "Mit Finances Donation",
					"supporter": full,
					"missionary": missionary,
					"fund": "General Support",
					"amount": amount,
					"donation_date": add_days(today(), offset),
					"payment_method": "Online" if i % 2 == 0 else "Check",
					"reference": ref,
				}
			).insert(ignore_permissions=True)


def _ensure_trips() -> None:
	for t in _TRIPS:
		if frappe.db.exists("Mit Trip", t["trip_name"]):
			continue
		frappe.get_doc(
			{
				"doctype": "Mit Trip",
				"trip_name": t["trip_name"],
				"status": t["status"],
				"destination": t["destination"],
				"missionary": t["missionary"],
				"total_goal": t["total_goal"],
				"start_date": add_days(today(), t["start"]),
				"end_date": add_days(today(), t["end"]),
			}
		).insert(ignore_permissions=True)


def _ensure_trip_applications() -> None:
	for name, email, trip, status in _APPLICANTS:
		if frappe.db.exists("Mit Trip Application", {"applicant_name": name, "trip": trip}):
			continue
		frappe.get_doc(
			{
				"doctype": "Mit Trip Application",
				"trip": trip,
				"applicant_name": name,
				"email": email,
				"status": status,
				"application_date": today(),
			}
		).insert(ignore_permissions=True)


def _ensure_prayer_letters() -> None:
	for title, missionary, offset, status in _PRAYER_LETTERS:
		if frappe.db.exists("Mit Correspondence Prayer Letter", title):
			continue
		frappe.get_doc(
			{
				"doctype": "Mit Correspondence Prayer Letter",
				"title": title,
				"missionary": missionary,
				"letter_date": add_days(today(), offset),
				"status": status,
				"content": f"<p>{title} — a brief update for our prayer partners.</p>",
			}
		).insert(ignore_permissions=True)


def _ensure_tasks() -> None:
	for title, task_type, tag, supporter, missionary, status, priority, due_offset in _TASKS:
		if frappe.db.exists("Mit Correspondence Ministry Task", {"title": title, "missionary": missionary}):
			continue
		frappe.get_doc(
			{
				"doctype": "Mit Correspondence Ministry Task",
				"title": title,
				"task_type": task_type,
				"tag": tag,
				"status": status,
				"priority": priority,
				"missionary": missionary,
				"supporter": supporter,
				"due_date": add_days(today(), due_offset),
			}
		).insert(ignore_permissions=True)


def _ensure_occasions() -> None:
	"""Give supporters birthdays and anniversaries that fall a set number of days from today.
	Only fills dates that are empty, so a real date someone entered is never changed."""
	for full, birthday, anniversary in _OCCASIONS:
		if not frappe.db.exists("Mit People Supporter", full):
			continue
		current = frappe.db.get_value("Mit People Supporter", full, ["birthday", "anniversary"], as_dict=True)
		values = {}
		if birthday is not None and not current.birthday:
			values["birthday"] = add_months(add_days(today(), birthday), -12 * 45)
		if anniversary is not None and not current.anniversary:
			values["anniversary"] = add_months(add_days(today(), anniversary), -12 * 20)
		if values:
			frappe.db.set_value("Mit People Supporter", full, values, update_modified=False)


def _ensure_church_visits() -> None:
	for church_name, missionary, offset, visit_type, status in _CHURCH_VISITS:
		church = _church_name(church_name)
		if not church:
			continue
		if frappe.db.exists(
			"Mit Deputation Church Visit", {"church": church, "missionary": missionary, "visit_type": visit_type}
		):
			continue
		frappe.get_doc(
			{
				"doctype": "Mit Deputation Church Visit",
				"church": church,
				"missionary": missionary,
				"visit_date": add_days(today(), offset),
				"visit_type": visit_type,
				"status": status,
			}
		).insert(ignore_permissions=True)


def _ensure_email_campaigns() -> None:
	"""A scheduled campaign with no supporter group, so it shows on the calendar but can never
	email anyone."""
	for title, missionary, offset in _EMAIL_CAMPAIGNS:
		if frappe.db.exists("Mit Correspondence Email Campaign", title):
			continue
		frappe.get_doc(
			{
				"doctype": "Mit Correspondence Email Campaign",
				"title": title,
				"missionary": missionary,
				"subject": title,
				"status": "Scheduled",
				"scheduled_date": add_days(today(), offset),
				"content": f"<p>{title}: sample content.</p>",
			}
		).insert(ignore_permissions=True)


def _ensure_furloughs() -> None:
	for missionary, start, end in _FURLOUGHS:
		if frappe.db.exists("Mit Furlough", {"missionary": missionary, "status": "Planned"}):
			continue
		frappe.get_doc(
			{
				"doctype": "Mit Furlough",
				"missionary": missionary,
				"status": "Planned",
				"furlough_type": "Scheduled",
				"start_date": add_days(today(), start),
				"end_date": add_days(today(), end),
			}
		).insert(ignore_permissions=True)
