# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Serve the Summary Home page at /desk/summary.

The page was renamed from `summary-home` to `summary`, so the desk writes its URL as
/desk/summary rather than /desk/summary/summary-home. Remove the records left behind:
the old `summary-home` Page, and the standard `Summary` Workspace the page replaced,
which would otherwise win the /desk/summary route over the page.
"""

import frappe


def execute():
	if frappe.db.exists("Page", "summary-home"):
		frappe.delete_doc("Page", "summary-home", force=True, ignore_permissions=True)

	workspace = frappe.db.get_value(
		"Workspace", "Summary", ["module", "public", "for_user"], as_dict=True
	)
	if workspace and workspace.module == "Mit Summary" and workspace.public and not workspace.for_user:
		frappe.delete_doc("Workspace", "Summary", force=True, ignore_permissions=True)
