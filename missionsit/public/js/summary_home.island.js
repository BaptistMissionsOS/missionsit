// This source code is freely given for the sake of the gospel (Matthew 10:8)
// and is licensed under MIT No Attribution (MIT-0).
//
// Overview — a Vue 3 "island" mounted into the Overview desk page.
// Vue is pulled from esm.sh so no build step is needed.
//
// The page reads like airmail from the field: a dispatch at the top (greeting, what is
// waiting, the verse), then the work waiting on you beside a support ledger, then trends,
// then a quiet row of links to every module.

import {
	createApp,
	h,
	reactive,
	computed,
	onMounted,
	onBeforeUnmount,
	ref,
	watch,
} from "https://esm.sh/vue@3.5.13";

const API = "missionsit.mit_summary.page.overview.overview.get_dashboard";

// Airmail blue, airmail red, sage, ochre, ink, then softer tints of the same.
const CHART_COLORS = ["#2D4E9C", "#C33A3A", "#3E7A5C", "#B7862B", "#5A6680", "#7F98D1", "#E08A8A"];

const CHART_TYPE_MAP = {
	Line: "line",
	Bar: "bar",
	Percentage: "percentage",
	Pie: "pie",
	Donut: "donut",
	Heatmap: "heatmap",
};

function formatNumber(value) {
	if (value === null || value === undefined || value === "") return "0";
	const n = Number(value);
	if (Number.isNaN(n)) return String(value);
	return n.toLocaleString(undefined, { maximumFractionDigits: Number.isInteger(n) ? 0 : 2 });
}

function icon(name, size = "sm") {
	return frappe.utils.icon(name || "square", size);
}

function openList(doctype, filters) {
	if (!doctype) return;
	if (filters && Object.keys(filters).length) {
		// A list filter takes `value` for equality and `[operator, value]` otherwise.
		frappe.route_options = Object.fromEntries(
			Object.entries(filters).map(([field, value]) => [field, value]),
		);
	}
	frappe.set_route("List", doctype);
}

function firstName() {
	const full = frappe.session.user_fullname || frappe.boot?.user?.first_name || "";
	return full.split(" ")[0] || "";
}

function greeting(date) {
	const hour = date.getHours();
	if (hour < 12) return __("Good morning");
	if (hour < 17) return __("Good afternoon");
	return __("Good evening");
}

function money(value, currency) {
	if (currency && window.format_currency) return format_currency(value, currency, 0);
	return formatNumber(Math.round(value || 0));
}

const SupportLevel = {
	props: { support: Object },
	setup(props) {
		return () => {
			const s = props.support;
			const pct = Math.max(0, s.percent || 0);
			const promisedPct = s.target ? Math.round(((s.committed + s.promised) / s.target) * 100) : 0;
			const label = s.who
				? __("{0}: {1}% supported", [s.who, pct])
				: s.missionaries > 1
				? __("{0} missionaries: {1}% supported together", [s.missionaries, pct])
				: __("{0}% supported", [pct]);
			return h("div", { class: "ov-support" }, [
				h("div", { class: "ov-support__line" }, [
					h("p", { class: "ov-support__label" }, label),
					h(
						"p",
						{ class: "ov-support__amounts" },
						__("{0} of {1} a month", [money(s.committed, s.currency), money(s.target, s.currency)]),
					),
				]),
				h(
					"div",
					{
						class: "ov-support__track",
						role: "progressbar",
						"aria-valuemin": 0,
						"aria-valuemax": 100,
						"aria-valuenow": Math.min(pct, 100),
						"aria-label": label,
					},
					[
						h("span", {
							class: "ov-support__promised",
							style: { width: `${Math.min(promisedPct, 100)}%` },
						}),
						h("span", { class: "ov-support__fill", style: { width: `${Math.min(pct, 100)}%` } }),
					],
				),
				s.promised
					? h(
							"p",
							{ class: "ov-support__note" },
							__("Another {0} a month is promised but not yet giving.", [money(s.promised, s.currency)]),
					  )
					: null,
			]);
		};
	},
};

const ComingUp = {
	props: { items: Array },
	setup(props) {
		const fmt = (iso) => {
			const d = new Date(`${iso}T00:00:00`);
			const today = new Date();
			today.setHours(0, 0, 0, 0);
			const days = Math.round((d - today) / 86400000);
			if (days === 0) return __("Today");
			if (days === 1) return __("Tomorrow");
			return d.toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short" });
		};
		return () =>
			h(
				"ol",
				{ class: "ov-coming" },
				props.items.map((item) =>
					h(
						"li",
						{ key: `${item.doctype}:${item.name}:${item.kind}`, class: "ov-coming__item" },
						h(
							"button",
							{
								type: "button",
								class: "ov-coming__button",
								onClick: () => frappe.set_route("Form", item.doctype, item.name),
							},
							[
								h("time", { class: "ov-coming__date", datetime: item.date }, fmt(item.date)),
								h("span", { class: "ov-coming__icon", innerHTML: icon(item.icon, "sm") }),
								h("span", { class: "ov-coming__text" }, [
									h("span", { class: "ov-coming__title" }, item.title),
									h("span", { class: "ov-coming__kind" }, __(item.kind)),
								]),
							],
						),
					),
				),
			);
	},
};

const Dispatch = {
	props: { verse: String, waiting: Number, support: Object },
	setup(props) {
		const now = new Date();
		const date = now.toLocaleDateString(undefined, {
			weekday: "long",
			day: "numeric",
			month: "long",
		});
		const name = firstName();
		return () =>
			h("header", { class: "ov-dispatch" }, [
				h("div", { class: "ov-dispatch__paper" }, [
					h("div", { class: "ov-dispatch__top" }, [
						h(
							"p",
							{ class: "ov-dispatch__hello" },
							name ? `${greeting(now)}, ${name}` : greeting(now),
						),
						h("time", { class: "ov-dispatch__date", datetime: now.toISOString() }, date),
					]),
					h(
						"h1",
						{ class: "ov-dispatch__headline" },
						props.waiting
							? props.waiting === 1
								? __("1 thing is waiting on you.")
								: __("{0} things are waiting on you.", [formatNumber(props.waiting)])
							: __("Nothing is waiting on you today."),
					),
					props.support ? h(SupportLevel, { support: props.support }) : null,
					props.verse
						? h("blockquote", { class: "ov-dispatch__verse", innerHTML: props.verse })
						: null,
				]),
			]);
	},
};

const WaitingRow = {
	props: { item: Object },
	setup(props) {
		return () => {
			const { item } = props;
			return h(
				"li",
				{ class: "ov-wait" },
				h(
					"button",
					{
						type: "button",
						class: "ov-wait__button",
						onClick: () => openList(item.doctype, item.filters),
					},
					[
						h("span", { class: "ov-wait__count" }, formatNumber(item.count)),
						h("span", { class: "ov-wait__label" }, item.label),
						h("span", { class: "ov-wait__icon", innerHTML: icon(item.icon, "sm") }),
					],
				),
			);
		};
	},
};

const LedgerLine = {
	props: { label: String, value: [Number, String], onOpen: Function },
	setup(props) {
		return () =>
			h(
				"li",
				{ class: "ov-ledger__line" },
				h("button", { type: "button", class: "ov-ledger__button", onClick: props.onOpen }, [
					h("span", { class: "ov-ledger__label" }, props.label),
					h("span", { class: "ov-ledger__leader", "aria-hidden": "true" }),
					h("span", { class: "ov-ledger__value" }, formatNumber(props.value)),
				]),
			);
	},
};

const ChartPanel = {
	props: { chart: Object },
	setup(props) {
		const host = ref(null);
		const empty = ref(false);

		function render() {
			if (!host.value) return;
			host.value.innerHTML = "";
			const labels = props.chart.labels || [];
			const datasets = props.chart.datasets || [];
			empty.value = !(labels.length && datasets.some((d) => (d.values || []).some((v) => v)));
			if (empty.value || !window.frappe?.Chart) return;
			const type = CHART_TYPE_MAP[props.chart.type] || "bar";
			new frappe.Chart(host.value, {
				data: { labels, datasets },
				type,
				// A pie's legend wraps beneath it on narrow screens, so give it room.
				height: ["pie", "donut", "percentage"].includes(type) ? 260 : 220,
				colors: CHART_COLORS,
				axisOptions: { xAxisMode: "tick", xIsSeries: type === "line" },
				barOptions: { spaceRatio: 0.45 },
				truncateLegends: true,
			});
		}

		onMounted(render);
		watch(() => props.chart, render, { deep: true });
		onBeforeUnmount(() => host.value && (host.value.innerHTML = ""));

		return () =>
			h("figure", { class: "ov-chart" }, [
				h("figcaption", { class: "ov-chart__title" }, props.chart.label),
				h("div", { class: "ov-chart__host", ref: host, hidden: empty.value }),
				empty.value
					? h("p", { class: "ov-chart__empty" }, __("Nothing recorded yet."))
					: null,
			]);
	},
};

const App = {
	setup() {
		const state = reactive({
			verse: "",
			support: null,
			coming_up: [],
			shortcuts: [],
			attention: [],
			cards: [],
			charts: [],
			website: {},
			loading: true,
			error: "",
		});

		async function load() {
			state.error = "";
			try {
				const data = await frappe.xcall(API, {}, "GET");
				Object.assign(state, {
					verse: data.verse || "",
					support: data.support || null,
					coming_up: data.coming_up || [],
					shortcuts: data.shortcuts || [],
					attention: data.attention || [],
					cards: data.cards || [],
					charts: data.charts || [],
					website: data.website || {},
				});
			} catch (err) {
				state.error = err.message || String(err);
			} finally {
				state.loading = false;
			}
		}

		onMounted(load);
		App.__reload = load;

		const waiting = computed(() =>
			state.attention.reduce((sum, item) => sum + (Number(item.count) || 0), 0),
		);
		// Rows with work keep the order the server gave; the all-clear ones fold into one line.
		const attention = computed(() => state.attention.filter((i) => i.count));
		const clear = computed(() => state.attention.filter((i) => !i.count).map((i) => i.label));
		const web = computed(() => [
			{ label: __("Donation pages"), value: state.website.donation_pages, doctype: "Mit Finances Donation Page" },
			{ label: __("Campaigns"), value: state.website.campaigns, doctype: "Mit Website Campaign" },
			{
				label: __("Missionary profiles"),
				value: state.website.missionary_profiles,
				doctype: "Mit Website Missionary Profile Page",
			},
		]);

		return () => {
			if (state.loading) return h("div", { class: "ov-status" }, __("Opening the mailbag…"));
			if (state.error)
				return h("div", { class: "ov-status ov-status--error" }, [
					h("p", {}, __("The overview could not load: {0}", [state.error])),
					h("button", { type: "button", class: "btn btn-default btn-sm", onClick: load }, __("Try again")),
				]);

			return h("div", { class: "ov" }, [
				h(Dispatch, { verse: state.verse, waiting: waiting.value, support: state.support }),

				h("div", { class: "ov-columns" }, [
					h("div", { class: "ov-main" }, [
						state.attention.length
							? h("section", { class: "ov-block", "aria-labelledby": "ov-waiting" }, [
									h("h2", { class: "ov-heading", id: "ov-waiting" }, __("Waiting on you")),
									attention.value.length
										? h(
												"ul",
												{ class: "ov-wait-list" },
												attention.value.map((item) =>
													h(WaitingRow, { item, key: `${item.doctype}:${item.label}` }),
												),
										  )
										: null,
									clear.value.length
										? h("p", { class: "ov-clear" }, [
												h("span", { class: "ov-clear__mark", innerHTML: icon("check", "sm") }),
												h(
													"span",
													{},
													__("All clear: {0}.", [
														clear.value
															.map((label, i) => (i ? label.toLowerCase() : label))
															.join(", "),
													]),
												),
										  ])
										: null,
							  ])
							: null,

						h("section", { class: "ov-block", "aria-labelledby": "ov-coming" }, [
							h("h2", { class: "ov-heading", id: "ov-coming" }, __("Coming up")),
							state.coming_up.length
								? h(ComingUp, { items: state.coming_up })
								: h(
										"p",
										{ class: "ov-quiet" },
										__("Nothing on the calendar for the next two weeks."),
								  ),
						]),
					]),

					h("section", { class: "ov-block ov-block--ledger", "aria-labelledby": "ov-ledger" }, [
						h("h2", { class: "ov-heading", id: "ov-ledger" }, __("Support ledger")),
						h(
							"ul",
							{ class: "ov-ledger" },
							state.cards.map((card) =>
								h(LedgerLine, {
									key: card.name,
									label: card.label,
									value: card.value,
									onOpen: () => openList(card.document_type),
								}),
							),
						),
						h("h3", { class: "ov-subheading" }, __("On the web")),
						h(
							"ul",
							{ class: "ov-ledger" },
							web.value.map((w) =>
								h(LedgerLine, {
									key: w.doctype,
									label: w.label,
									value: w.value,
									onOpen: () => openList(w.doctype),
								}),
							),
						),
					]),
				]),

				state.charts.length
					? h("section", { class: "ov-block", "aria-labelledby": "ov-trends" }, [
							h("h2", { class: "ov-heading", id: "ov-trends" }, __("Trends")),
							h(
								"div",
								{ class: "ov-charts" },
								state.charts.map((chart) => h(ChartPanel, { chart, key: chart.name })),
							),
					  ])
					: null,

				state.shortcuts.length
					? h("nav", { class: "ov-modules", "aria-label": __("Modules") }, [
							h("h2", { class: "ov-heading" }, __("Go to")),
							h(
								"ul",
								{ class: "ov-modules__list" },
								state.shortcuts.map((s) =>
									h(
										"li",
										{ key: s.sidebar },
										h(
											"button",
											{
												type: "button",
												class: "ov-module",
												onClick: () => frappe.set_route(frappe.router.slug(s.sidebar)),
											},
											[
												h("span", { class: "ov-module__icon", innerHTML: icon(s.icon, "sm") }),
												h("span", {}, s.title),
											],
										),
									),
								),
							),
					  ])
					: null,
			]);
		};
	},
};

export function mount(target) {
	const el = typeof target === "string" ? document.querySelector(target) : target;
	const app = createApp(App);
	const instance = app.mount(el);
	return { app, instance, reload: () => App.__reload?.() };
}
