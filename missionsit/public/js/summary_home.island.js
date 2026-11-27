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
	nextTick,
} from "https://esm.sh/vue@3.5.13";

const API = "missionsit.mit_summary.page.overview.overview.get_dashboard";
const TREND_API = "missionsit.mit_summary.page.overview.overview.get_trend";

// Airmail blue for every trend: one series at a time needs one colour, and no legend. Read from
// the stylesheet so dark mode gets its lighter blue.
function chartColor(el) {
	return getComputedStyle(el).getPropertyValue("--ov-blue").trim() || "#2D4E9C";
}

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

const CALENDAR_API = "missionsit.mit_summary.page.overview.overview.get_calendar";
const PLAN_API = "missionsit.mit_summary.page.overview.overview.plan_action";

const RANGES = [
	{ days: 14, label: "2 weeks" },
	{ days: 30, label: "30 days" },
	{ days: 90, label: "90 days" },
];

const GROUPS = [
	{ key: "all", label: "All" },
	{ key: "visits", label: "Visits" },
	{ key: "occasions", label: "Birthdays" },
	{ key: "trips", label: "Trips" },
	{ key: "furlough", label: "Furlough" },
	{ key: "emails", label: "Emails" },
];

function dayLabel(iso) {
	const d = new Date(`${iso}T00:00:00`);
	const today = new Date();
	today.setHours(0, 0, 0, 0);
	const days = Math.round((d - today) / 86400000);
	if (days === 0) return __("Today");
	if (days === 1) return __("Tomorrow");
	return d.toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short" });
}

// What a person can do with an item, before and after doing it.
const ACTIONS = {
	card: { verb: "Plan a card", done: "Card planned", icon: "mail-plus" },
	follow_up: { verb: "Plan follow-up", done: "Follow-up planned", icon: "phone-forwarded" },
};

// Coming up: a range switch, filter chips with counts, items grouped by day, and one action on
// the items that have one. Opens on the fortnight the dashboard already sent.
const Calendar = {
	props: { initial: Array, later: Array },
	setup(props) {
		const range = ref(14);
		const group = ref("all");
		const items = ref(props.initial || []);
		const loading = ref(false);
		const failed = ref("");
		const busy = ref("");
		const cache = new Map([[14, props.initial || []]]);

		const counts = computed(() => {
			const c = { all: items.value.length };
			for (const i of items.value) c[i.group] = (c[i.group] || 0) + 1;
			return c;
		});
		// Only the filters that have something in this range, so no chip leads nowhere.
		const groups = computed(() => GROUPS.filter((g) => g.key === "all" || counts.value[g.key]));
		const shown = computed(() =>
			group.value === "all" ? items.value : items.value.filter((i) => i.group === group.value),
		);
		const days = computed(() => byDay(shown.value));

		async function pickRange(daysAhead) {
			if (daysAhead === range.value) return;
			range.value = daysAhead;
			failed.value = "";
			if (cache.has(daysAhead)) {
				items.value = cache.get(daysAhead);
			} else {
				loading.value = true;
				try {
					const data = await frappe.xcall(CALENDAR_API, { days: daysAhead }, "GET");
					cache.set(daysAhead, data);
					if (range.value === daysAhead) items.value = data;
				} catch (err) {
					failed.value = err.message || String(err);
				} finally {
					loading.value = false;
				}
			}
			if (!counts.value[group.value]) group.value = "all";
		}

		async function plan(item) {
			const key = `${item.doctype}:${item.name}:${item.kind}`;
			busy.value = key;
			try {
				const res = await frappe.xcall(PLAN_API, {
					doctype: item.doctype,
					name: item.name,
					kind: item.kind,
					date: item.date,
				});
				// The same occasion can sit in more than one cached range.
				for (const list of cache.values())
					for (const other of list)
						if (other.doctype === item.doctype && other.name === item.name && other.kind === item.kind)
							other.planned = true;
				item.planned = true;
				frappe.show_alert?.({ message: __(res.label), indicator: "green" });
			} catch (err) {
				frappe.show_alert?.({ message: err.message || String(err), indicator: "red" });
			} finally {
				busy.value = "";
			}
		}

		function actionButton(item) {
			const action = ACTIONS[item.action];
			if (!action) return null;
			if (item.planned)
				return h("span", { class: "ov-cal__done" }, [
					h("span", { innerHTML: icon("check", "sm") }),
					__(action.done),
				]);
			const key = `${item.doctype}:${item.name}:${item.kind}`;
			return h(
				"button",
				{
					type: "button",
					class: "ov-cal__action",
					disabled: busy.value === key,
					onClick: () => plan(item),
				},
				[h("span", { innerHTML: icon(action.icon, "sm") }), __(action.verb)],
			);
		}

		function list(dayGroups, later = false) {
			return h(
				"ol",
				{ class: ["ov-cal__days", later && "ov-cal__days--later"] },
				dayGroups.map((day) =>
					h("li", { key: day.date, class: "ov-cal__day" }, [
						h("time", { class: "ov-cal__date", datetime: day.date }, dayLabel(day.date)),
						h(
							"ul",
							{ class: "ov-cal__items" },
							day.items.map((item) =>
								h("li", { key: `${item.doctype}:${item.name}:${item.kind}`, class: "ov-cal__item" }, [
									h("span", { class: "ov-cal__icon", innerHTML: icon(item.icon, "sm") }),
									h(
										"button",
										{
											type: "button",
											class: "ov-cal__open",
											onClick: () => frappe.set_route("Form", item.doctype, item.name),
										},
										[
											h("span", { class: "ov-cal__title" }, item.title),
											h("span", { class: "ov-cal__kind" }, __(item.kind)),
										],
									),
									actionButton(item),
								]),
							),
						),
					]),
				),
			);
		}

		function byDay(entries) {
			const out = [];
			for (const item of entries) {
				const last = out[out.length - 1];
				if (last && last.date === item.date) last.items.push(item);
				else out.push({ date: item.date, items: [item] });
			}
			return out;
		}

		return () =>
			h("section", { class: "ov-block ov-cal", "aria-labelledby": "ov-coming" }, [
				h("div", { class: "ov-cal__bar" }, [
					h("h2", { class: "ov-heading ov-cal__heading", id: "ov-coming" }, __("Coming up")),
					h(
						"div",
						{ class: "ov-switch ov-switch--small", role: "radiogroup", "aria-label": __("How far ahead") },
						RANGES.map((r) =>
							h(
								"button",
								{
									key: r.days,
									type: "button",
									role: "radio",
									"aria-checked": String(r.days === range.value),
									class: ["ov-switch__option", r.days === range.value && "is-on"],
									onClick: () => pickRange(r.days),
								},
								__(r.label),
							),
						),
					),
				]),
				items.value.length > 1 && groups.value.length > 2
					? h(
							"div",
							{ class: "ov-chips", role: "group", "aria-label": __("Show only") },
							groups.value.map((g) =>
								h(
									"button",
									{
										key: g.key,
										type: "button",
										"aria-pressed": String(g.key === group.value),
										class: ["ov-chip", g.key === group.value && "is-on"],
										onClick: () => (group.value = g.key),
									},
									[__(g.label), h("span", { class: "ov-chip__count" }, counts.value[g.key])],
								),
							),
					  )
					: null,
				h("div", { class: ["ov-cal__body", loading.value && "is-loading"] }, [
					failed.value
						? h("p", { class: "ov-quiet" }, __("Coming up could not load: {0}", [failed.value]))
						: items.value.length
						? list(days.value)
						: h("p", { class: "ov-quiet" }, [
								range.value === 14
									? __("Nothing on the calendar for the next two weeks.")
									: __("Nothing on the calendar for the next {0} days.", [range.value]),
								range.value === 14 && props.later?.length ? " " + __("Next up:") : "",
						  ]),
					!items.value.length && range.value === 14 && props.later?.length
						? list(byDay(props.later), true)
						: null,
				]),
			]);
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

// One chart for every trend. A switch picks the subject (donations, pledges, trips) and a
// dropdown picks how to slice it; each view is fetched once and kept.
const TrendPanel = {
	props: { menu: Array },
	setup(props) {
		const subject = ref(props.menu[0]?.key);
		const view = ref(props.menu[0]?.views[0]?.key);
		const trend = ref(null);
		const loading = ref(false);
		const failed = ref("");
		const host = ref(null);
		const cache = new Map();

		const views = computed(() => props.menu.find((m) => m.key === subject.value)?.views || []);
		const empty = computed(() => trend.value && !trend.value.values.some((v) => v));

		function amount(value) {
			const t = trend.value;
			if (t?.money) return money(value, t.currency);
			return formatNumber(value);
		}

		function draw() {
			if (!host.value) return;
			host.value.innerHTML = "";
			const t = trend.value;
			if (!t || empty.value || !window.frappe?.Chart) return;
			new frappe.Chart(host.value, {
				data: { labels: t.labels, datasets: [{ name: "", values: t.values }] },
				type: t.type === "line" ? "line" : "bar",
				height: 260,
				colors: [chartColor(host.value)],
				axisOptions: { xAxisMode: "tick", xIsSeries: t.type === "line", shortenYAxisNumbers: t.money ? 1 : 0 },
				// Few categories make very wide bars, so space them out.
				barOptions: { spaceRatio: t.labels.length <= 4 ? 0.75 : 0.5 },
				lineOptions: { regionFill: 1, dotSize: 4 },
				tooltipOptions: { formatTooltipY: (v) => amount(v) },
			});
		}

		async function load() {
			const key = `${subject.value}:${view.value}`;
			failed.value = "";
			if (cache.has(key)) {
				trend.value = cache.get(key);
				return;
			}
			loading.value = true;
			try {
				const data = await frappe.xcall(TREND_API, { subject: subject.value, view: view.value }, "GET");
				cache.set(key, data);
				// Only show it if the reader has not moved on while it loaded.
				if (key === `${subject.value}:${view.value}`) trend.value = data;
			} catch (err) {
				failed.value = err.message || String(err);
			} finally {
				loading.value = false;
			}
		}

		function pickSubject(key) {
			if (key === subject.value) return;
			subject.value = key;
			view.value = views.value[0]?.key;
		}

		watch([subject, view], load);
		watch(trend, () => nextTick(draw));
		onMounted(load);
		onBeforeUnmount(() => host.value && (host.value.innerHTML = ""));

		return () => {
			const current = views.value.find((v) => v.key === view.value);
			return h("section", { class: "ov-block ov-trends", "aria-labelledby": "ov-trends" }, [
				h("div", { class: "ov-trends__bar" }, [
					h("h2", { class: "ov-heading ov-trends__heading", id: "ov-trends" }, __("Trends")),
					h(
						"div",
						{ class: "ov-switch", role: "radiogroup", "aria-label": __("Show trends for") },
						props.menu.map((m) =>
							h(
								"button",
								{
									key: m.key,
									type: "button",
									role: "radio",
									"aria-checked": String(m.key === subject.value),
									class: ["ov-switch__option", m.key === subject.value && "is-on"],
									onClick: () => pickSubject(m.key),
								},
								__(m.label),
							),
						),
					),
					h("label", { class: "ov-trends__view" }, [
						h("span", { class: "sr-only" }, __("View")),
						h(
							"select",
							{
								class: "form-control input-sm ov-select",
								value: view.value,
								onChange: (e) => (view.value = e.target.value),
							},
							views.value.map((v) => h("option", { key: v.key, value: v.key }, __(v.label))),
						),
					]),
				]),
				h("div", { class: ["ov-trends__panel", loading.value && "is-loading"] }, [
					trend.value && !empty.value
						? h("p", { class: "ov-trends__summary" }, [
								h("span", { class: "ov-trends__total" }, amount(trend.value.total)),
								h("span", {}, current ? __(current.total) : ""),
						  ])
						: null,
					failed.value
						? h("p", { class: "ov-trends__empty" }, __("This trend could not load: {0}", [failed.value]))
						: empty.value
						? h("p", { class: "ov-trends__empty" }, __("Nothing recorded yet."))
						: null,
					h("div", { class: "ov-trends__host", ref: host, hidden: !!(empty.value || failed.value) }),
				]),
			]);
		};
	},
};

const App = {
	setup() {
		const state = reactive({
			verse: "",
			support: null,
			coming_up: [],
			coming_later: [],
			shortcuts: [],
			attention: [],
			cards: [],
			trends: [],
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
					coming_later: data.coming_later || [],
					shortcuts: data.shortcuts || [],
					attention: data.attention || [],
					cards: data.cards || [],
					trends: data.trends || [],
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

				// Full width, like Trends, so a longer range grows down the page rather than
				// leaving a gap beside the ledger.
				h(Calendar, { initial: state.coming_up, later: state.coming_later }),

				state.trends.length ? h(TrendPanel, { menu: state.trends }) : null,

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
