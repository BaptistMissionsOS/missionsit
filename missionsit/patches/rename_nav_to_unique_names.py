# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Give the module sidebars and workspaces names no other app on the site uses.

Sidebar, Workspace, Page and Number Card names are global to a site, and churchit ships
sidebars and workspaces called People, Finances, Help, Ministries, Prayers, Settings and
Summary, plus a Number Card called Missionaries. On a site with both apps, whichever migrated
last would take the other's record and its /desk/<name> route.

Migrate has already imported the renamed files. Remove the old records, but only the ones
this app owns, so another app's record of the same name is left alone. Then import the dock
that links to the new names and carry the desktop icons over.
"""

import os

import frappe
from frappe.modules.import_file import import_file_by_path

RENAMES = {
	"Finances": "Stewardship",
	"Help": "Helps",
	"Ministries": "Outreach",
	"People": "Peoples",
	"Prayers": "Prayer Wall",
	"Settings": "Configs",
	"Summary": "Overview",
}


def execute():
	modules = set(frappe.get_all("Module Def", filters={"app_name": "missionsit"}, pluck="name"))

	def owned(doctype, name, field="module"):
		return frappe.db.exists(doctype, name) and frappe.db.get_value(doctype, name, field) in modules

	for old in RENAMES:
		for doctype in ("Sidebar", "Workspace"):
			if owned(doctype, old):
				frappe.delete_doc(doctype, old, force=True, ignore_permissions=True)

	if owned("Page", "summary"):
		frappe.delete_doc("Page", "summary", force=True, ignore_permissions=True)
	if owned("Number Card", "Missionaries"):
		frappe.delete_doc("Number Card", "Missionaries", force=True, ignore_permissions=True)

	app_path = frappe.get_app_path("missionsit")
	import_file_by_path(os.path.join(app_path, "dock", "missionsit", "missionsit.json"), force=True)

	for old, new in RENAMES.items():
		icon = frappe.db.get_value("Desktop Icon", old, ["app", "link_to"], as_dict=True)
		if not icon or icon.app != "missionsit":
			continue
		if frappe.db.exists("Desktop Icon", new):
			frappe.delete_doc("Desktop Icon", old, force=True, ignore_permissions=True)
		else:
			frappe.rename_doc("Desktop Icon", old, new, force=True, show_alert=False)
			frappe.db.set_value("Desktop Icon", new, {"label": new, "link_to": new}, update_modified=False)

	frappe.clear_cache()
