# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Member Portal module pages: the desk's modules, read-only, for a signed-in member.

The modules and the DocTypes in each come from the app's own sidebars, in the order of the
navbar, so the portal shows the same structure as the desk. Only those DocTypes can be read
through here, and every read goes through Frappe's permission checks: the member's roles, the
app's permission query conditions and permission levels. A member sees in the portal exactly
what they could see in the desk, and nothing more.
"""

import glob
import json
import os

import frappe
from frappe import _

# Modules the portal leaves out: Overview is the desk's own home, and Web App is the portal.
SKIPPED_SIDEBARS = {"Overview", "Web App"}
LIST_PAGE = 20
LIST_COLUMNS = 4
TEXT_TYPES = {"Text Editor", "HTML Editor", "Markdown Editor", "Text", "Long Text", "Code", "JSON"}
SKIPPED_TYPES = {
	"Section Break",
	"Column Break",
	"Tab Break",
	"HTML",
	"Button",
	"Password",
	"Fold",
	"Heading",
	"Image",
	"Geolocation",
	"Signature",
}


@frappe.whitelist()
def get_modules() -> list[dict]:
	"""The modules this member can open, each with the DocTypes in it they can read."""
	_require_sign_in()
	modules = []
	for sidebar in _app_sidebars():
		doctypes = [d for d in sidebar["doctypes"] if frappe.has_permission(d["doctype"], "read")]
		if doctypes:
			modules.append({**sidebar, "doctypes": doctypes})
	return modules


@frappe.whitelist()
def get_records(doctype: str, search: str | None = None, start: int = 0) -> dict:
	"""One page of *doctype*'s records the member may read, newest first, with the columns
	the desk shows in its list view."""
	meta = _readable(doctype)
	columns = _list_columns(meta)
	fields = ["name", "modified", *[c["fieldname"] for c in columns]]
	title = meta.title_field if meta.title_field and meta.title_field not in fields else None
	if title:
		fields.append(title)

	filters = {}
	if search:
		filters[meta.title_field or "name"] = ["like", f"%{search.strip()}%"]
	rows = frappe.get_list(
		doctype,
		filters=filters,
		fields=fields,
		order_by="modified desc",
		start=int(start),
		page_length=LIST_PAGE + 1,
	)
	return {
		"doctype": doctype,
		"title_field": meta.title_field or "name",
		"columns": columns,
		"rows": rows[:LIST_PAGE],
		"more": len(rows) > LIST_PAGE,
	}


@frappe.whitelist()
def get_record(doctype: str, name: str) -> dict:
	"""One record as read-only sections of label and value, keeping only the fields the member
	may read."""
	meta = _readable(doctype)
	doc = frappe.get_doc(doctype, name)
	doc.check_permission("read")

	sections, current = [], {"label": None, "fields": []}
	for df in meta.fields:
		if df.fieldtype in ("Section Break", "Tab Break"):
			if current["fields"]:
				sections.append(current)
			current = {"label": _(df.label) if df.label else None, "fields": []}
			continue
		if df.hidden or df.fieldtype in SKIPPED_TYPES:
			continue
		if not doc.has_permlevel_access_to(df.fieldname, df, permission_type="read"):
			continue
		value = doc.get(df.fieldname)
		if value in (None, "", []) or (df.fieldtype == "Check" and not value):
			continue
		entry = {"fieldname": df.fieldname, "label": _(df.label), "fieldtype": df.fieldtype, "options": df.options}
		if df.fieldtype in ("Table", "Table MultiSelect"):
			entry.update(_table(df, value))
		elif df.fieldtype in ("Attach", "Attach Image"):
			# Only files anyone may load; a private file would show as a broken link.
			if not str(value).startswith("/files/"):
				continue
			entry["value"] = value
		elif df.fieldtype == "Check":
			entry["value"] = _("Yes")
		else:
			entry["value"] = value if df.fieldtype in TEXT_TYPES else frappe.format_value(value, df, doc)
		current["fields"].append(entry)
	if current["fields"]:
		sections.append(current)

	user_type = frappe.db.get_value("User", frappe.session.user, "user_type")
	return {
		"doctype": doctype,
		"name": doc.name,
		"title": doc.get(meta.title_field) if meta.title_field else doc.name,
		"modified": str(doc.modified),
		"sections": sections,
		"desk_url": frappe.utils.get_url_to_form(doctype, doc.name) if user_type == "System User" else None,
	}


# --- Helpers ---------------------------------------------------------------------------------


def _require_sign_in():
	if frappe.session.user == "Guest":
		frappe.throw(_("Sign in to open the Member Portal."), frappe.PermissionError)


def _app_sidebars() -> list[dict]:
	"""The app's sidebars that link to its own DocTypes, in the navbar's order."""
	app_path = frappe.get_app_path("missionsit")
	modules = set(frappe.get_all("Module Def", filters={"app_name": "missionsit"}, pluck="name"))
	order = _dock_order(app_path)

	sidebars = []
	for path in glob.glob(os.path.join(app_path, "*", "sidebar", "*", "*.json")):
		with open(path) as f:
			doc = json.load(f)
		if doc.get("doctype") != "Sidebar" or doc["name"] in SKIPPED_SIDEBARS:
			continue
		doctypes, seen = [], set()
		for item in doc.get("items", []):
			doctype = item.get("link_to")
			if item.get("type") != "Link" or item.get("link_type") != "DocType" or doctype in seen:
				continue
			meta = frappe.get_meta(doctype) if frappe.db.exists("DocType", doctype) else None
			if not meta or meta.module not in modules or meta.istable or meta.issingle:
				continue
			seen.add(doctype)
			doctypes.append({"doctype": doctype, "label": _(item.get("label") or doctype)})
		if doctypes:
			sidebars.append(
				{
					"name": doc["name"],
					"title": _(doc.get("title") or doc["name"]),
					"slug": frappe.scrub(doc["name"]).replace("_", "-"),
					"icon": doc.get("header_icon"),
					"doctypes": doctypes,
				}
			)
	return sorted(sidebars, key=lambda s: (order.get(s["name"], len(order)), s["title"]))


def _dock_order(app_path: str) -> dict[str, int]:
	try:
		with open(os.path.join(app_path, "dock", "missionsit", "missionsit.json")) as f:
			items = json.load(f).get("items", [])
	except (OSError, ValueError):
		return {}
	return {item.get("link_to"): i for i, item in enumerate(items)}


def _readable(doctype: str):
	"""*doctype*'s meta, if it is one of the portal's DocTypes and the member may read it."""
	_require_sign_in()
	allowed = {d["doctype"] for s in _app_sidebars() for d in s["doctypes"]}
	if doctype not in allowed:
		frappe.throw(_("{0} is not part of the Member Portal.").format(doctype), frappe.PermissionError)
	if not frappe.has_permission(doctype, "read"):
		frappe.throw(_("You do not have access to {0}.").format(_(doctype)), frappe.PermissionError)
	return frappe.get_meta(doctype)


def _list_columns(meta) -> list[dict]:
	"""The DocType's list-view fields, without the ones a short row cannot show."""
	columns = []
	for df in meta.fields:
		if not df.in_list_view or df.hidden or df.fieldtype in SKIPPED_TYPES | TEXT_TYPES:
			continue
		if df.fieldtype in ("Table", "Table MultiSelect", "Attach", "Attach Image") or df.permlevel:
			continue
		if df.fieldname == meta.title_field:
			continue
		columns.append({"fieldname": df.fieldname, "label": _(df.label), "fieldtype": df.fieldtype, "options": df.options})
		if len(columns) == LIST_COLUMNS:
			break
	return columns


def _table(df, rows) -> dict:
	"""A child table as a few columns of formatted values."""
	child = frappe.get_meta(df.options)
	cols = [
		c
		for c in child.fields
		if c.in_list_view and not c.hidden and c.fieldtype not in SKIPPED_TYPES | TEXT_TYPES
	][:LIST_COLUMNS]
	return {
		"columns": [{"fieldname": c.fieldname, "label": _(c.label)} for c in cols],
		"rows": [{c.fieldname: frappe.format_value(row.get(c.fieldname), c, row) for c in cols} for row in rows],
	}
