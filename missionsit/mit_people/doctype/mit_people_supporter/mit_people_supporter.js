// This source code is freely given for the sake of the gospel (Matthew 10:8)
// and is licensed under MIT No Attribution (MIT-0).

frappe.ui.form.on("Mit People Supporter", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Log Interaction"), () => {
				frappe.new_doc("Mit People Interaction", {
					supporter: frm.doc.name,
					missionary: frm.doc.missionary,
				});
			}, __("Actions"));

			frm.add_custom_button(__("New Task"), () => {
				frappe.new_doc("Mit Correspondence Ministry Task", {
					supporter: frm.doc.name,
					missionary: frm.doc.missionary,
				});
			}, __("Actions"));

			frm.add_custom_button(__("New Donation"), () => {
				frappe.new_doc("Mit Finances Donation", {
					supporter: frm.doc.name,
					missionary: frm.doc.missionary,
				});
			}, __("Actions"));
		}
	},
});
