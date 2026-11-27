# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Read endpoints for the public web app at /missions.

Everything a guest can call returns only what is meant to be public: published missionary
profiles, active donation pages and campaigns, and trips that are planned or open. Each reads
with `frappe.get_all` and an explicit field list, so a field added to a DocType later never
leaks by accident. The member portal is the one exception: it needs a signed-in user and shows
only that user's own records, matched by email.
"""

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit

UPCOMING_TRIP_STATUSES = ("Planning", "Open", "Full")

# The church map's MapLibre style. OpenFreeMap needs no key; to use your own tile server, set
# "missions_map_style" in site_config.json to its style URL.
DEFAULT_MAP_STYLE = "https://tiles.openfreemap.org/styles/positron"


@frappe.whitelist(allow_guest=True)
def get_site() -> dict:
	"""Portal settings, who is signed in, and a short count of the work."""
	portal = frappe.get_cached_doc("Mit Website Portal")
	profiles = _published_profiles()
	countries = {p["field_country"] for p in profiles if p.get("field_country")}
	return {
		"title": portal.portal_title or _("Missions"),
		"welcome": portal.welcome_message or "",
		"footer": portal.footer_text or "",
		"enable_signups": bool(portal.enable_signups),
		"enable_donations": bool(portal.enable_donations),
		"enable_trip_applications": bool(portal.enable_trip_applications),
		"user": _session_user(),
		"map_style": frappe.conf.get("missions_map_style") or DEFAULT_MAP_STYLE,
		"counts": {
			"missionaries": len(profiles),
			"countries": len(countries),
			"trips": len(_upcoming_trips()),
		},
	}


@frappe.whitelist(allow_guest=True)
def get_home() -> dict:
	"""The home page in one call: upcoming departures, missionaries, and ways to give."""
	return {
		"departures": _upcoming_trips(limit=8),
		"missionaries": _published_profiles(limit=6),
		"campaigns": _active_campaigns(limit=3),
		"pages": _donation_pages(limit=3),
	}


@frappe.whitelist(allow_guest=True)
def get_missionaries() -> list[dict]:
	return _published_profiles()


@frappe.whitelist(allow_guest=True)
def get_missionary(slug: str) -> dict:
	"""One published profile by its route (or record name), with ways to give to that
	missionary and their upcoming trips."""
	profile = next(
		(p for p in _published_profiles(with_bio=True) if slug in (p["slug"], p["name"])),
		None,
	)
	if not profile:
		frappe.throw(_("That missionary profile is not published."), frappe.DoesNotExistError)
	missionary = profile["missionary"]
	return {
		"profile": profile,
		"pages": [p for p in _donation_pages() if p["missionary"] == missionary],
		"trips": [t for t in _upcoming_trips() if t["missionary"] == missionary],
	}


@frappe.whitelist(allow_guest=True)
def get_trips() -> list[dict]:
	return _upcoming_trips(with_description=True)


@frappe.whitelist(allow_guest=True)
def get_give() -> dict:
	return {"pages": _donation_pages(), "campaigns": _active_campaigns()}


@frappe.whitelist()
def get_portal() -> dict:
	"""The signed-in member's own giving and trip applications, matched by their email."""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Sign in to see your member portal."), frappe.PermissionError)
	email = frappe.db.get_value("User", user, "email") or user
	supporters = frappe.get_all("Mit People Supporter", filters={"email": email}, pluck="name")

	donations, recurring, pledges = [], [], []
	if supporters:
		donations = frappe.get_all(
			"Mit Finances Donation",
			filters={"supporter": ["in", supporters]},
			fields=["name", "donation_date", "amount", "currency", "fund", "missionary"],
			order_by="donation_date desc",
			limit_page_length=50,
		)
		recurring = frappe.get_all(
			"Mit Finances Recurring Donation",
			filters={"supporter": ["in", supporters], "status": ["in", ["Active", "Paused"]]},
			fields=["name", "amount", "currency", "frequency", "status", "next_payment_date", "missionary"],
		)
		pledges = frappe.get_all(
			"Mit Finances Pledge",
			filters={"supporter": ["in", supporters], "status": ["in", ["Promised", "Giving", "Paused"]]},
			fields=["name", "amount", "currency", "frequency", "status", "missionary"],
		)
	applications = frappe.get_all(
		"Mit Trip Application",
		filters={"email": email},
		fields=["name", "trip", "status", "application_date"],
		order_by="application_date desc",
	)

	names = _missionary_names([r.missionary for r in donations + recurring + pledges])
	for row in donations + recurring + pledges:
		row.missionary_name = names.get(row.missionary, row.missionary)

	year_start = frappe.utils.getdate().replace(month=1, day=1)
	return {
		"user": _session_user(),
		"linked": bool(supporters),
		"given_this_year": sum(
			d.amount or 0 for d in donations if d.donation_date and d.donation_date >= year_start
		),
		"donations": donations,
		"recurring": recurring,
		"pledges": pledges,
		"applications": applications,
	}


# Fields a visitor may fill in on a church submission. Everything else (status, review, the
# church it becomes) is set here or by the reviewer, never by the form.
SUBMISSION_FIELDS = (
	"church_name",
	"pastor_name",
	"affiliation",
	"address_line",
	"city",
	"state_province",
	"postal_code",
	"country",
	"phone",
	"email",
	"website",
	"service_times",
	"language",
)
MAX_CHURCHES_PER_SUBMISSION = 100


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=10, seconds=60 * 60)
def submit_churches(churches, submitter_name=None, submitter_email=None, website_url=None) -> dict:
	"""Add one church, or a list of them, to the directory's review queue. No sign-in needed.

	Each church becomes a Church Submission in Pending Review; nothing reaches the directory
	until a reviewer approves it. `website_url` is a honeypot: the form hides it from people, so
	a value there means a bot filled the form, and the request is accepted and dropped.
	"""
	if website_url:
		return {"received": 0}

	if isinstance(churches, str):
		churches = frappe.parse_json(churches)
	if not isinstance(churches, list) or not churches:
		frappe.throw(_("Add at least one church."))
	if len(churches) > MAX_CHURCHES_PER_SUBMISSION:
		frappe.throw(
			_("Send at most {0} churches at a time. Split the list and send the rest after.").format(
				MAX_CHURCHES_PER_SUBMISSION
			)
		)
	if submitter_email and not frappe.utils.validate_email_address(submitter_email):
		frappe.throw(_("{0} is not an email address.").format(submitter_email))

	source = "List Upload" if len(churches) > 1 else "Single Submission"
	batch = frappe.generate_hash(length=10) if len(churches) > 1 else None
	received = 0
	for row in churches:
		if not isinstance(row, dict):
			continue
		values = {f: (str(row.get(f) or "").strip()[:140] or None) for f in SUBMISSION_FIELDS}
		if not values["church_name"]:
			continue
		notes = []
		# Country is a link; an unknown name would fail the insert, so keep it as a note instead.
		if values["country"] and not frappe.db.exists("Country", values["country"]):
			notes.append(_("Country given: {0}").format(values["country"]))
			values["country"] = None
		for field in ("email", "website"):
			if values[field] and not (
				frappe.utils.validate_email_address(values[field]) if field == "email" else values[field].startswith(("http://", "https://"))
			):
				notes.append(_("{0} given: {1}").format(field.title(), values[field]))
				values[field] = None
		frappe.get_doc(
			{
				"doctype": "Mit Directory Church Submission",
				**values,
				"status": "Pending Review",
				"source": source,
				"submission_batch": batch,
				"submitter_name": (submitter_name or "").strip()[:140] or None,
				"submitter_email": submitter_email or None,
				"review_notes": "\n".join(notes) or None,
			}
		).insert(ignore_permissions=True)
		received += 1

	if not received:
		frappe.throw(_("Every church needs a name."))
	return {"received": received}


# --- Helpers ---------------------------------------------------------------------------------


def _session_user() -> dict | None:
	user = frappe.session.user
	if user == "Guest":
		return None
	info = frappe.db.get_value(
		"User", user, ["full_name", "first_name", "user_image", "user_type"], as_dict=True
	)
	return {
		"name": user,
		"full_name": info.full_name or user,
		"first_name": info.first_name or (info.full_name or user).split(" ")[0],
		"image": info.user_image,
		"is_desk_user": info.user_type == "System User",
	}


def _missionary_names(names: list[str]) -> dict[str, str]:
	names = [n for n in set(names) if n]
	if not names:
		return {}
	return dict(
		frappe.get_all(
			"Mit People Missionary",
			filters={"name": ["in", names]},
			fields=["name", "missionary_name"],
			as_list=True,
		)
	)


def _public_file(url: str | None) -> str | None:
	"""Only files anyone may load. A private attachment would show as a broken image."""
	return url if url and url.startswith("/files/") else None


def _published_profiles(limit: int | None = None, with_bio: bool = False) -> list[dict]:
	fields = ["name", "page_title", "route", "missionary", "headline", "profile_image", "field_summary"]
	if with_bio:
		fields.append("bio")
	rows = frappe.get_all(
		"Mit Website Missionary Profile Page",
		filters={"is_published": 1},
		fields=fields,
		order_by="page_title asc",
		limit_page_length=limit or 0,
	)
	people = {
		m.name: m
		for m in frappe.get_all(
			"Mit People Missionary",
			filters={"name": ["in", [r.missionary for r in rows if r.missionary]]},
			fields=["name", "missionary_name", "status", "field_country"],
		)
	}
	profiles = []
	for row in rows:
		person = people.get(row.missionary) or frappe._dict()
		profiles.append(
			{
				"name": row.name,
				"slug": (row.route or row.name).strip("/").split("/")[-1],
				"missionary": row.missionary,
				"display_name": person.missionary_name or row.page_title,
				"headline": row.headline,
				"image": _public_file(row.profile_image),
				"summary": row.field_summary,
				"status": person.status,
				"field_country": person.field_country,
				**({"bio": row.bio} if with_bio else {}),
			}
		)
	return profiles


def _upcoming_trips(limit: int | None = None, with_description: bool = False) -> list[dict]:
	fields = ["name", "status", "destination", "start_date", "end_date", "missionary"]
	if with_description:
		fields.append("description")
	rows = frappe.get_all(
		"Mit Trip",
		filters={
			"status": ["in", list(UPCOMING_TRIP_STATUSES)],
			"start_date": [">=", frappe.utils.today()],
		},
		fields=fields,
		order_by="start_date asc",
		limit_page_length=limit or 0,
	)
	portal_open = bool(frappe.db.get_single_value("Mit Website Portal", "enable_trip_applications"))
	names = _missionary_names([r.missionary for r in rows])
	return [
		{
			**row,
			"missionary_name": names.get(row.missionary),
			"can_apply": portal_open and row.status == "Open",
		}
		for row in rows
	]


def _active_campaigns(limit: int | None = None) -> list[dict]:
	rows = frappe.get_all(
		"Mit Website Campaign",
		filters={"status": "Active"},
		fields=["name", "campaign_name", "campaign_type", "goal_amount", "amount_raised", "end_date", "missionary"],
		order_by="end_date asc",
		limit_page_length=limit or 0,
	)
	names = _missionary_names([r.missionary for r in rows])
	return [{**row, "missionary_name": names.get(row.missionary)} for row in rows]


def _donation_pages(limit: int | None = None) -> list[dict]:
	"""Active donation pages with a slug, each with what has been given through it."""
	rows = frappe.get_all(
		"Mit Finances Donation Page",
		filters={"is_active": 1, "slug": ["is", "set"]},
		fields=["name", "title", "slug", "missionary", "goal_amount", "currency", "allow_recurring"],
		order_by="title asc",
		limit_page_length=limit or 0,
	)
	raised = {}
	if rows:
		for gift in frappe.get_all(
			"Mit Finances Donation",
			filters={"donation_page": ["in", [r.name for r in rows]]},
			fields=["donation_page", "amount"],
		):
			raised[gift.donation_page] = raised.get(gift.donation_page, 0) + (gift.amount or 0)
	names = _missionary_names([r.missionary for r in rows])
	return [
		{**row, "raised": raised.get(row.name, 0), "missionary_name": names.get(row.missionary)}
		for row in rows
	]
