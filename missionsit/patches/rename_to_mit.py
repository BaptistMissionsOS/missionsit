"""Rename every Missions * module and doctype to the Mit * convention."""

import frappe

DOCTYPE_RENAMES = {
    "Budget": "Mit Finances Budget",
    "Business Contact": "Mit Tentmaker Business Contact",
    "Churches": "Mit Deputation Churches",
    "Church": "Mit Directory Church",
    "Church Accommodation": "Mit Directory Church Accommodation",
    "Church Note": "Mit Directory Church Note",
    "Church Submission": "Mit Directory Church Submission",
    "Church Verification": "Mit Directory Church Verification",
    "Church Visit": "Mit Deputation Church Visit",
    "Correspondence Log": "Mit Correspondence Log",
    "Deputation Schedule": "Mit Deputation Schedule",
    "Directory Access Request": "Mit Directory Access Request",
    "Donation": "Mit Finances Donation",
    "Donation Page": "Mit Finances Donation Page",
    "Email": "Mit Correspondence Email",
    "Email Campaign": "Mit Correspondence Email Campaign",
    "Expense": "Mit Finances Expense",
    "FAQ": "Mit Help Faq",
    "Financial Period": "Mit Finances Financial Period",
    "Fund": "Mit Finances Fund",
    "Furlough": "Mit Furlough",
    "General Ledger": "Mit Finances General Ledger",
    "Help Articles": "Mit Help Articles",
    "Interaction": "Mit People Interaction",
    "Marketplace Listing": "Mit Marketplace Listing",
    "Ministry Activity": "Mit Ministries Activity",
    "Ministry Partner": "Mit Ministries Partner",
    "Ministry Project": "Mit Ministries Project",
    "Ministry Task": "Mit Correspondence Ministry Task",
    "Missions Missionary": "Mit People Missionary",
    "Organization": "Mit People Organization",
    "Partnership Stage": "Mit Deputation Partnership Stage",
    "Pledge": "Mit Finances Pledge",
    "Prayer Letter": "Mit Correspondence Prayer Letter",
    "Prayer Request": "Mit Prayer Request",
    "Prayer Team": "Mit Prayer Team",
    "Prayer Team Member": "Mit Prayer Team Member",
    "Prayer Update": "Mit Prayer Update",
    "Presentation": "Mit Deputation Presentation",
    "Recurring Donation": "Mit Finances Recurring Donation",
    "Skills Services": "Mit Tentmaker Skills Services",
    "Supporter": "Mit People Supporter",
    "Supporter Group": "Mit People Supporter Group",
    "Supporter Referral": "Mit People Supporter Referral",
    "Tentmaker Job": "Mit Tentmaker Job",
    "Trip": "Mit Trip",
    "Trip Application": "Mit Trip Application",
    "Trip Expense": "Mit Trip Expense",
    "Trip Participant": "Mit Trip Participant",
}

MODULE_RENAMES = {
    "Missions Correspondence": "Mit Correspondence",
    "Missions Deputation": "Mit Deputation",
    "Missions Directory": "Mit Directory",
    "Missions Finances": "Mit Finances",
    "Missions Furlough": "Mit Furlough",
    "Missions Help": "Mit Help",
    "Missions Marketplace": "Mit Marketplace",
    "Missions Ministries": "Mit Ministries",
    "Missions People": "Mit People",
    "Missions Prayers": "Mit Prayers",
    "Missions Setup": "Mit Setup",
    "Missions Summary": "Mit Summary",
    "Missions Tentmaker": "Mit Tentmaker",
    "Missions Trip": "Mit Trip",
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
    for old, new in DOCTYPE_RENAMES.items():
        if frappe.db.exists("DocType", old) and not frappe.db.exists("DocType", new):
            frappe.rename_doc("DocType", old, new, force=True, merge=False)
    for old, new in MODULE_RENAMES.items():
        for dt in MODULE_LINKED_DOCTYPES:
            table = f"tab{dt}"
            if not frappe.db.table_exists(table, cached=False):
                continue
            frappe.db.sql(f"UPDATE `{table}` SET module = %s WHERE module = %s", (new, old))
        if frappe.db.exists("Module Def", old) and not frappe.db.exists("Module Def", new):
            frappe.rename_doc("Module Def", old, new, force=True, merge=False)
    frappe.db.commit()
    frappe.cache.delete_value("app_modules")
    frappe.client_cache.delete_value("installed_app_modules")
    frappe.setup_module_map(include_all_apps=False)
