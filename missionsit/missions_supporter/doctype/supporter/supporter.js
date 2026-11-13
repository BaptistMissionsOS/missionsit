// This source code is freely given for the sake of the gospel (Matthew 10:8)
// and is licensed under MIT No Attribution (MIT-0).

frappe.ui.form.on("Supporter", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Log Interaction"), () => {
				frappe.new_doc("Interaction", {
					supporter: frm.doc.name,
					missionary: frm.doc.missionary,
				});
			}, __("Actions"));

			frm.add_custom_button(__("New Task"), () => {
				frappe.new_doc("Ministry Task", {
					supporter: frm.doc.name,
					missionary: frm.doc.missionary,
				});
			}, __("Actions"));

			frm.add_custom_button(__("New Donation"), () => {
				frappe.new_doc("Donation", {
					supporter: frm.doc.name,
					missionary: frm.doc.missionary,
				});
			}, __("Actions"));
		}
	},
});
