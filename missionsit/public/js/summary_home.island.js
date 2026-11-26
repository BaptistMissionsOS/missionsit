// This source code is freely given for the sake of the gospel (Matthew 10:8)
// and is licensed under MIT No Attribution (MIT-0).
//
// Summary Home — a Vue 3 "island" mounted into the Summary Home desk page,
// styled after frappe-ui. Vue is pulled from esm.sh so no build step is needed.
//
// Sections: verse, needs attention (list), at a glance (numbers), trends (charts), website.

import {
	createApp,
	h,
	reactive,
	onMounted,
	onBeforeUnmount,
	ref,
	watch,
} from "https://esm.sh/vue@3.5.13";

const API = "missionsit.mit_summary.page.summary.summary.get_dashboard";

const CHART_COLORS = [
	"#2490ef",
	"#2ecc71",
	"#f59e0b",
	"#8b5cf6",
	"#ef4444",
	"#14b8a6",
	"#ec4899",
	"#64748b",
];

function formatNumber(value) {
	if (value === null || value === undefined) return "—";
	if (typeof value !== "number") return String(value);
	if (Math.abs(value) >= 10000) return value.toLocaleString();
	return Number.isInteger(value) ? String(value) : value.toFixed(2);
}

function icon(name, size = "md") {
	return frappe.utils.icon(name || "square", size);
}

function go(route) {
	window.location.href = route;
}

function listRoute(doctype, filters) {
	const base = `/app/${frappe.router.slug(doctype)}/view/list`;
	if (!filters) return base;
	const parts = Object.entries(filters).map(([field, value]) => {
		const serialized = Array.isArray(value) ? JSON.stringify(value) : value;
		return `${encodeURIComponent(field)}=${encodeURIComponent(serialized)}`;
	});
	return `${base}?${parts.join("&")}`;
}

const CHART_TYPE_MAP = {
	Line: "line",
	Bar: "bar",
	Percentage: "percentage",
	Pie: "pie",
	Donut: "donut",
	Heatmap: "heatmap",
};

const Section = {
	props: { title: String },
	setup(props, { slots }) {
		return () =>
			h("section", { class: "sh-section" }, [
				h("h2", { class: "sh-section__title" }, props.title),
				slots.default?.(),
			]);
	},
};

const ShortcutTile = {
	props: { shortcut: Object },
	setup(props) {
		const open = () => frappe.set_route(frappe.router.slug(props.shortcut.sidebar));
		return () =>
			h(
				"button",
				{
					type: "button",
					class: `sh-tile sh-tile--${props.shortcut.tone || "blue"}`,
					onClick: open,
					title: props.shortcut.title,
				},
				[
					h("span", {
						class: "sh-tile__icon",
						innerHTML: icon(props.shortcut.icon, "md"),
					}),
					h("span", { class: "sh-tile__label" }, props.shortcut.title),
				],
			);
	},
};

const AttentionRow = {
	props: { item: Object },
	setup(props) {
		const open = () => go(listRoute(props.item.doctype, props.item.filters));
		return () =>
			h(
				"button",
				{
					type: "button",
					class: `sh-row sh-row--${props.item.tone || "blue"}`,
					onClick: open,
				},
				[
					h("span", {
						class: "sh-row__icon",
						innerHTML: icon(props.item.icon, "sm"),
					}),
					h("span", { class: "sh-row__label" }, props.item.label),
					h(
						"span",
						{ class: "sh-row__count" },
						formatNumber(props.item.count),
					),
					h("span", {
						class: "sh-row__chev",
						innerHTML: icon("chevron-right", "xs"),
					}),
				],
			);
	},
};

const NumberCardTile = {
	props: { card: Object },
	setup(props) {
		const open = () => {
			if (props.card.document_type)
				frappe.set_route("List", props.card.document_type);
		};
		return () =>
			h(
				"button",
				{
					type: "button",
					class: "sh-number",
					onClick: open,
				},
				[
					h("span", { class: "sh-number__label" }, props.card.label),
					h(
						"span",
						{ class: "sh-number__value" },
						formatNumber(props.card.value),
					),
				],
			);
	},
};

const ChartCard = {
	props: { chart: Object },
	setup(props) {
		const host = ref(null);
		let instance = null;

		function render() {
			if (!host.value) return;
			host.value.innerHTML = "";
			instance = null;
			const labels = props.chart.labels || [];
			const datasets = props.chart.datasets || [];
			const hasData =
				labels.length &&
				datasets.some((d) => (d.values || []).some((v) => v));
			if (!hasData) {
				host.value.innerHTML = `<p class="sh-empty">${__("No data yet.")}</p>`;
				return;
			}
			const type = CHART_TYPE_MAP[props.chart.type] || "bar";
			instance = new frappe.Chart(host.value, {
				data: { labels, datasets },
				type,
				height: 240,
				colors: CHART_COLORS,
				axisOptions: { xAxisMode: "tick", xIsSeries: type === "line" },
				truncateLegends: true,
			});
		}

		onMounted(render);
		watch(() => props.chart, render, { deep: true });
		onBeforeUnmount(() => {
			instance = null;
			if (host.value) host.value.innerHTML = "";
		});

		return () =>
			h("article", { class: "sh-card" }, [
				h("h3", { class: "sh-card__title" }, props.chart.label),
				h("div", { class: "sh-chart-host", ref: host }),
			]);
	},
};

const WebsiteRow = {
	props: { label: String, count: Number, icon: String, href: String },
	setup(props) {
		const open = () => {
			if (!props.href) return;
			frappe.set_route(props.href);
		};
		return () =>
			h(
				"button",
				{ type: "button", class: "sh-web", onClick: open },
				[
					h("span", {
						class: "sh-web__icon",
						innerHTML: icon(props.icon, "sm"),
					}),
					h("span", { class: "sh-web__label" }, props.label),
					h(
						"span",
						{ class: "sh-web__count" },
						formatNumber(props.count),
					),
				],
			);
	},
};

const App = {
	setup() {
		const state = reactive({
			verse: "",
			shortcuts: [],
			attention: [],
			cards: [],
			charts: [],
			website: {},
			loading: true,
			error: "",
		});

		async function load() {
			state.loading = true;
			state.error = "";
			try {
				const data = await frappe.xcall(API, {}, "GET");
				state.verse = data.verse || "";
				state.shortcuts = data.shortcuts || [];
				state.attention = data.attention || [];
				state.cards = data.cards || [];
				state.charts = data.charts || [];
				state.website = data.website || {};
			} catch (err) {
				state.error = err.message || String(err);
			} finally {
				state.loading = false;
			}
		}

		onMounted(load);
		App.__reload = load;

		return () => {
			if (state.loading && !state.cards.length)
				return h("div", { class: "sh-loading" }, __("Loading…"));
			if (state.error)
				return h("div", { class: "sh-error" }, [
					h("p", {}, state.error),
					h(
						"button",
						{
							type: "button",
							class: "sh-button",
							onClick: load,
						},
						__("Try again"),
					),
				]);

			const children = [];

			if (state.verse)
				children.push(
					h("div", {
						class: "sh-verse",
						innerHTML: state.verse,
					}),
				);

			if (state.shortcuts.length)
				children.push(
					h(Section, { title: __("Modules") }, () =>
						h(
							"div",
							{ class: "sh-tiles" },
							state.shortcuts.map((s) =>
								h(ShortcutTile, { shortcut: s, key: s.sidebar }),
							),
						),
					),
				);

			if (state.cards.length)
				children.push(
					h(Section, { title: __("At a Glance") }, () =>
						h(
							"div",
							{ class: "sh-numbers" },
							state.cards.map((card) =>
								h(NumberCardTile, { card, key: card.name }),
							),
						),
					),
				);

			if (state.attention.length)
				children.push(
					h(Section, { title: __("Needs Attention") }, () =>
						h(
							"div",
							{ class: "sh-card sh-card--rows" },
							state.attention.map((item) =>
								h(AttentionRow, {
									item,
									key: `${item.doctype}:${item.label}`,
								}),
							),
						),
					),
				);

			if (state.charts.length)
				children.push(
					h(Section, { title: __("Trends") }, () =>
						h(
							"div",
							{ class: "sh-charts" },
							state.charts.map((chart) =>
								h(ChartCard, { chart, key: chart.name }),
							),
						),
					),
				);

			const website = state.website || {};
			const websiteItems = [
				{
					label: __("Donation Pages"),
					count: website.donation_pages || 0,
					icon: "credit-card",
					href: "Mit Finances Donation Page",
				},
				{
					label: __("Campaigns"),
					count: website.campaigns || 0,
					icon: "megaphone",
					href: "Mit Website Campaign",
				},
				{
					label: __("Missionary Profiles"),
					count: website.missionary_profiles || 0,
					icon: "user-round",
					href: "Mit Website Missionary Profile Page",
				},
			];
			children.push(
				h(Section, { title: __("Website") }, () =>
					h(
						"div",
						{ class: "sh-card sh-card--rows" },
						websiteItems.map((w) =>
							h(WebsiteRow, {
								label: w.label,
								count: w.count,
								icon: w.icon,
								href: w.href,
								key: w.label,
							}),
						),
					),
				),
			);

			return h("div", { class: "sh-stack" }, children);
		};
	},
};

export function mount(target) {
	const el = typeof target === "string" ? document.querySelector(target) : target;
	const app = createApp(App);
	const instance = app.mount(el);
	return {
		app,
		instance,
		reload: () => App.__reload?.(),
	};
}
