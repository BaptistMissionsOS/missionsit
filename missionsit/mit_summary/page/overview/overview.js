// This source code is freely given for the sake of the gospel (Matthew 10:8)
// and is licensed under MIT No Attribution (MIT-0).

// Summary Home: the desk page that hosts a Vue3 + frappe-ui island with the dashboard.

frappe.pages["overview"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Overview"),
		single_column: true,
	});
	const cacheBust = Date.now();
	const existingCss = document.getElementById("mit-summary-home-css");
	if (existingCss) existingCss.remove();
	const link = document.createElement("link");
	link.id = "mit-summary-home-css";
	link.rel = "stylesheet";
	link.href = `/assets/missionsit/css/summary_home.css?v=${cacheBust}`;
	document.head.appendChild(link);
	const $mount = $('<div id="mit-summary-home" class="mit-summary-home"></div>').appendTo(
		page.body,
	);
	wrapper.summary_page = page;

	import(`/assets/missionsit/js/summary_home.island.js?v=${cacheBust}`)
		.then((mod) => {
			wrapper.summary_island = mod.mount($mount[0]);
		})
		.catch((err) => {
			$mount.html(
				`<div class="mit-summary-error">${frappe.utils.escape_html(
					__("Could not load the Summary island: {0}", [err.message || err]),
				)}</div>`,
			);
		});
};

frappe.pages["overview"].on_page_show = function (wrapper) {
	wrapper.summary_island?.reload?.();
};
