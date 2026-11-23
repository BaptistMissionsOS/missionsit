import frappe

# Each old module is folded into whichever new module absorbed its doctypes.
MODULE_REMAP = {
	"Missions Organization": "Missions People",
	"Missions Missionary": "Missions People",
	"Missions Supporter": "Missions People",
	"Missions Supporter Group": "Missions People",
	"Missions Supporter Referral": "Missions People",
	"Missions Interaction": "Missions People",
	"Missions Church": "Missions Deputation",
	"Missions Church Visit": "Missions Deputation",
	"Missions Partnership Stage": "Missions Deputation",
	"Missions Donation": "Missions Finances",
	"Missions Donation Page": "Missions Finances",
	"Missions Fund": "Missions Finances",
	"Missions Pledge": "Missions Finances",
	"Missions Recurring Donation": "Missions Finances",
	"Missions Payments": "Missions Finances",
	"Missions Email Campaign": "Missions Correspondence",
	"Missions Ministry Task": "Missions Correspondence",
	"Missions Prayer Letter": "Missions Correspondence",
	"Missions Trip Application": "Missions Trip",
	"Missions Trip Participant": "Missions Trip",
	"Missions Campaign": "Mit Website",
}

MODULE_LINKED_DOCTYPES = (
	"DocType",
	"Workspace",
	"Dashboard",
	"Dashboard Chart",
	"Number Card",
	"Report",
	"Print Format",
	"Role",
	"Custom Field",
	"Property Setter",
	"Kanban Board",
)


def execute():
	for old, new in MODULE_REMAP.items():
		for dt in MODULE_LINKED_DOCTYPES:
			table = f"tab{dt}"
			if not frappe.db.table_exists(table, cached=False):
				continue
			frappe.db.sql(
				f"UPDATE `{table}` SET module = %s WHERE module = %s",
				(new, old),
			)

	frappe.db.sql(
		"DELETE FROM `tabModule Def` WHERE name IN %(names)s",
		{"names": tuple(MODULE_REMAP.keys())},
	)

	# The `Missionary` DocType was dropped along with its module; its Number Card
	# lingers because migrate's orphan sweep does not reach Number Card rows.
	frappe.db.delete("Number Card", {"document_type": "Missionary"})

	frappe.db.commit()

	# Bust the cache so sync_all re-reads modules.txt instead of the stale list.
	frappe.cache.delete_value("app_modules")
	frappe.client_cache.delete_value("installed_app_modules")
	frappe.setup_module_map(include_all_apps=False)
