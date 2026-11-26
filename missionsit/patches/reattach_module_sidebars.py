# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Put every shipped sidebar back under the module it ships in.

The first scaffolds kept every sidebar (People, Trips, Finances, ...) in the Summary module.
When each moved into its own module, migrate skipped re-importing it, since the file was not
newer than the record, so the records stayed under Mit Summary. Frappe then gave each real
module a computed sidebar named after the module, which is why the desk showed "Mit People"
at /desk/mit-people/people instead of "People" at /desk/people.

Force-import each shipped sidebar so its module, title and items match the file, then drop
any other standard sidebar this app owns that no file ships.
"""

import glob
import json
import os

import frappe
from frappe.modules.import_file import import_file_by_path


def execute():
	app_path = frappe.get_app_path("missionsit")
	shipped = {}
	for path in sorted(glob.glob(os.path.join(app_path, "*", "sidebar", "*", "*.json"))):
		with open(path) as f:
			doc = json.load(f)
		if doc.get("doctype") == "Sidebar":
			shipped[doc["name"]] = path

	for path in shipped.values():
		import_file_by_path(path, force=True, reset_permissions=True)

	app_modules = set(frappe.get_all("Module Def", filters={"app_name": "missionsit"}, pluck="name"))
	stale = frappe.get_all(
		"Sidebar",
		filters={"standard": 1, "name": ["not in", list(shipped)]},
		fields=["name", "module", "app"],
	)
	for sidebar in stale:
		if sidebar.app == "missionsit" or sidebar.module in app_modules:
			# Delete the row only. Its exported folder, if any, is not shipped by the app.
			frappe.db.delete("Sidebar Item", {"parent": sidebar.name, "parenttype": "Sidebar"})
			frappe.db.delete("Sidebar", {"name": sidebar.name})

	frappe.clear_cache()
