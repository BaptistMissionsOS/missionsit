# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Rename the `Mit Help FAQ` DocType to `Mit Help Faq`.

The desk turns a list URL such as /desk/help/mit-help-faq back into a DocType name by
title-casing the slug, which gives `Mit Help Faq`. MariaDB finds the DocType row whatever its
case, but table names are case-sensitive, so the query for `tabMit Help Faq` failed with a
server error. A name that title-cases to itself avoids the round trip going wrong.

`rename_doc` allows a case-only rename, and renames the table and every link to it.
"""

import frappe


def execute():
	old, new = "Mit Help FAQ", "Mit Help Faq"
	if frappe.db.get_value("DocType", old, "name") != old:
		return

	frappe.rename_doc("DocType", old, new, force=True, show_alert=False)
	frappe.db.commit()
