// This source code is freely given for the sake of the gospel (Matthew 10:8)
// and is licensed under MIT No Attribution (MIT-0).

frappe.ui.form.on("Missionary", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("View Supporters"), () => {
				frappe.set_route("List", "Supporter", { missionary: frm.doc.name });
			});
		}
	},
});
