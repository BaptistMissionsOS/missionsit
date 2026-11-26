# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Rename the Mit Website shell to Web App, so it routes at /desk/web-app.

Frappe ships its own `Website` module, so the shell cannot take that name. Drop the old
`Mit Website` sidebar and workspace records, import their `Web App` replacements and the
dock that links to them, and carry the desktop icon over to the new label.
"""

import os

import frappe
from frappe.modules.import_file import import_file_by_path


def execute():
	for doctype in ("Sidebar", "Workspace"):
		if frappe.db.exists(doctype, "Mit Website"):
			frappe.delete_doc(doctype, "Mit Website", force=True, ignore_permissions=True)

	app_path = frappe.get_app_path("missionsit")
	for path in (
		("mit_website", "sidebar", "web_app", "web_app.json"),
		("mit_website", "workspace", "web_app", "web_app.json"),
		("dock", "missionsit", "missionsit.json"),
	):
		import_file_by_path(os.path.join(app_path, *path), force=True, reset_permissions=True)

	if frappe.db.exists("Desktop Icon", "Mit Website") and not frappe.db.exists("Desktop Icon", "Web App"):
		frappe.rename_doc("Desktop Icon", "Mit Website", "Web App", force=True, show_alert=False)
	if frappe.db.exists("Desktop Icon", "Web App"):
		frappe.db.set_value(
			"Desktop Icon", "Web App", {"label": "Web App", "link_to": "Web App"}, update_modified=False
		)

	frappe.clear_cache()
