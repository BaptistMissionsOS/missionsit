# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Make the Web App home a frappe-ui island page at /desk/web-app.

The Web App sidebar's Home now opens the `web-app` Page instead of the `Web App` Workspace.
Migrate has imported the page and the sidebar; remove the workspace, which would otherwise
still answer at /desk/web-app ahead of the page.
"""

import frappe
from frappe.modules.import_file import import_file_by_path


def execute():
	workspace = frappe.db.get_value("Workspace", "Web App", ["module", "for_user"], as_dict=True)
	if workspace and workspace.module == "Mit Website" and not workspace.for_user:
		frappe.delete_doc("Workspace", "Web App", force=True, ignore_permissions=True)

	import_file_by_path(
		frappe.get_app_path("missionsit", "mit_website", "sidebar", "web_app", "web_app.json"), force=True
	)
	frappe.clear_cache()
