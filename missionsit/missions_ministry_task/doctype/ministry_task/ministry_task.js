// This source code is freely given for the sake of the gospel (Matthew 10:8)
// and is licensed under MIT No Attribution (MIT-0).

frappe.ui.form.on("Ministry Task", {
	supporter(frm) {
		if (frm.doc.supporter && !frm.doc.missionary) {
			frappe.db.get_value("Supporter", frm.doc.supporter, "missionary").then(({ message }) => {
				if (message && message.missionary) {
					frm.set_value("missionary", message.missionary);
				}
			});
		}
	},

	status(frm) {
		if (frm.doc.status === "Completed" && !frm.doc.completed_on) {
			frm.set_value("completed_on", frappe.datetime.now_datetime());
		}
	},
});
