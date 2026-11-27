// This source code is freely given for the sake of the gospel (Matthew 10:8)
// and is licensed under MIT No Attribution (MIT-0).

// Web App home: the desk page that hosts a Vue 3 + frappe-ui island for running the public
// web app at /missions. The island lives in public/js/web_app_home.island.js so it can be
// redesigned without touching this loader.

frappe.pages["web-app"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Web App"),
		single_column: true,
	});
	const cacheBust = Date.now();
	document.getElementById("mit-web-app-home-css")?.remove();
	const link = document.createElement("link");
	link.id = "mit-web-app-home-css";
	link.rel = "stylesheet";
	link.href = `/assets/missionsit/css/web_app_home.css?v=${cacheBust}`;
	document.head.appendChild(link);
	const $mount = $('<div class="mit-web-app-home"></div>').appendTo(page.body);

	import(`/assets/missionsit/js/web_app_home.island.js?v=${cacheBust}`)
		.then((mod) => {
			wrapper.web_app_island = mod.mount($mount[0]);
		})
		.catch((err) => {
			$mount.html(
				`<div class="wa-status">${frappe.utils.escape_html(
					__("The Web App home could not load: {0}", [err.message || err]),
				)}</div>`,
			);
		});
};

frappe.pages["web-app"].on_page_show = function (wrapper) {
	wrapper.web_app_island?.reload?.();
};
