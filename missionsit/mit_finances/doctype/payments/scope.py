# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Role-scoped query helpers shared across doctypes.

Organization Admin sees every Missionary under the Organization that owns their user record.
Missionary sees only their own Missionary record.
"""

import frappe


def missionary_permission_query(user: str) -> str:
	"""Narrow the Missionary list by the caller's role scope."""
	roles = frappe.get_roles(user)
	if "System Manager" in roles:
		return ""
	if "Organization Admin" in roles:
		organizations = _organizations_for_user(user)
		if not organizations:
			return "1=0"
		quoted = ", ".join(frappe.db.escape(o) for o in organizations)
		return f"`tabMit People Missionary`.`organization` in ({quoted})"
	if "Missionary" in roles:
		missionary = frappe.db.get_value("Mit People Missionary", {"user": user}, "name")
		if not missionary:
			return "1=0"
		return f"`tabMit People Missionary`.`name` = {frappe.db.escape(missionary)}"
	return ""


def _organizations_for_user(user: str) -> list[str]:
	"""Return Organization names where *user* is listed as the primary admin or contact."""
	return frappe.get_all(
		"Mit People Organization",
		filters={"admin_user": user},
		pluck="name",
	)
