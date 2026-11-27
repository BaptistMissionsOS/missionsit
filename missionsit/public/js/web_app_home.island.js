// This source code is freely given for the sake of the gospel (Matthew 10:8)
// and is licensed under MIT No Attribution (MIT-0).
//
// Web App home — a Vue 3 "island" mounted into the Web App desk page. It runs the public web
// app at /missions: whether it is switched on, what is published on it, and what is missing.
// Vue is pulled from esm.sh so no build step is needed, the same as the Overview island.

import { createApp, h, reactive, computed, onMounted } from "https://esm.sh/vue@3.5.13";

const API = "missionsit.mit_website.page.web_app.web_app";

function money(value, currency) {
	if (window.format_currency) return format_currency(value || 0, currency, 0);
	return Number(value || 0).toLocaleString();
}

function day(iso) {
	if (!iso) return "";
	return frappe.datetime.str_to_user(String(iso).slice(0, 10));
}

function icon(name, size = "sm") {
	return frappe.utils.icon(name, size);
}

function openList(doctype, filters) {
	if (filters && Object.keys(filters).length) frappe.route_options = { ...filters };
	frappe.set_route("List", doctype);
}

const Switch = {
	props: { item: Object, disabled: Boolean, busy: Boolean },
	emits: ["toggle"],
	setup(props, { emit }) {
		return () =>
			h(
				"button",
				{
					type: "button",
					role: "switch",
					"aria-checked": String(props.item.on),
					class: ["wa-switch", props.item.on && "is-on"],
					disabled: props.disabled || props.busy,
					onClick: () => emit("toggle", props.item),
				},
				[
					h("span", { class: "wa-switch__track", "aria-hidden": "true" }, h("span", { class: "wa-switch__thumb" })),
					h("span", { class: "wa-switch__text" }, [
						h("span", { class: "wa-switch__label" }, props.item.label),
						h("span", { class: "wa-switch__state" }, props.item.on ? __("On") : __("Off")),
					]),
				],
			);
	},
};

const Goal = {
	props: { raised: Number, goal: Number, currency: String },
	setup(props) {
		return () => {
			const pct = props.goal ? Math.min(100, Math.round(((props.raised || 0) / props.goal) * 100)) : 0;
			return h("div", { class: "wa-goal" }, [
				h("div", { class: "wa-goal__line" }, [
					h("span", { class: "wa-goal__raised" }, money(props.raised, props.currency)),
					props.goal
						? h("span", { class: "wa-goal__of" }, __("{0}% of {1}", [pct, money(props.goal, props.currency)]))
						: null,
				]),
				props.goal
					? h(
							"div",
							{ class: "wa-goal__track", role: "progressbar", "aria-valuenow": pct, "aria-valuemin": 0, "aria-valuemax": 100 },
							h("span", { class: "wa-goal__fill", style: { width: `${pct}%` } }),
					  )
					: null,
			]);
		};
	},
};

const App = {
	setup() {
		const state = reactive({ data: null, loading: true, error: "", busy: "" });

		async function load() {
			state.error = "";
			try {
				state.data = await frappe.xcall(`${API}.get_home`, {}, "GET");
			} catch (err) {
				state.error = err.message || String(err);
			} finally {
				state.loading = false;
			}
		}

		async function toggle(item) {
			state.busy = item.field;
			try {
				const res = await frappe.xcall(`${API}.set_switch`, { field: item.field, on: item.on ? 0 : 1 });
				item.on = res.on;
				frappe.show_alert({
					message: res.on ? __("{0} turned on", [item.label]) : __("{0} turned off", [item.label]),
					indicator: res.on ? "green" : "orange",
				});
			} catch (err) {
				frappe.show_alert({ message: err.message || String(err), indicator: "red" });
			} finally {
				state.busy = "";
			}
		}

		onMounted(load);
		App.__reload = load;

		const gaps = computed(() => (state.data?.checklist || []).filter((c) => c.count));
		const done = computed(() => (state.data?.checklist || []).filter((c) => !c.count));

		return () => {
			if (state.loading) return h("div", { class: "wa-status" }, __("Loading the web app…"));
			if (state.error)
				return h("div", { class: "wa-status wa-status--error" }, [
					h("p", {}, __("The Web App home could not load: {0}", [state.error])),
					h("button", { type: "button", class: "btn btn-default btn-sm", onClick: load }, __("Try again")),
				]);
			const d = state.data;
			const address = `${window.location.origin}${d.url}`;

			return h("div", { class: "wa" }, [
				// The site card: where the web app lives and its three switches.
				h("section", { class: "wa-site", "aria-labelledby": "wa-site" }, [
					h("div", { class: "wa-site__head" }, [
						h("div", {}, [
							h("h1", { class: "wa-site__title", id: "wa-site" }, d.title),
							h("a", { class: "wa-site__url", href: d.url, target: "_blank", rel: "noopener" }, address),
						]),
						h("div", { class: "wa-site__actions" }, [
							h(
								"button",
								{
									type: "button",
									class: "wa-button",
									onClick: () => navigator.clipboard?.writeText(address).then(() => frappe.show_alert({ message: __("Link copied"), indicator: "green" })),
								},
								[h("span", { innerHTML: icon("copy") }), __("Copy link")],
							),
							h("a", { class: "wa-button wa-button--primary", href: d.url, target: "_blank", rel: "noopener" }, [
								__("Open the web app"),
								h("span", { innerHTML: icon("external-link") }),
							]),
						]),
					]),
					h(
						"div",
						{ class: "wa-switches" },
						d.switches.map((item) =>
							h(Switch, { key: item.field, item, disabled: !d.can_edit, busy: state.busy === item.field, onToggle: toggle }),
						),
					),
					d.can_edit ? null : h("p", { class: "wa-note" }, __("Only people who can edit the portal settings can change these.")),
				]),

				// What is published.
				h(
					"ul",
					{ class: "wa-published", "aria-label": __("Published on the web app") },
					d.published.map((p) =>
						h(
							"li",
							{ key: p.label },
							h("button", { type: "button", class: "wa-published__item", onClick: () => openList(p.doctype) }, [
								h("span", { class: "wa-published__value" }, [
									String(p.value),
									p.of !== undefined ? h("span", { class: "wa-published__of" }, ` / ${p.of}`) : null,
								]),
								h("span", { class: "wa-published__label" }, p.label),
							]),
						),
					),
				),

				h("div", { class: "wa-columns" }, [
					h("div", { class: "wa-main" }, [
						h("section", { "aria-labelledby": "wa-gaps" }, [
							h("h2", { class: "wa-heading", id: "wa-gaps" }, __("Before it looks finished")),
							gaps.value.length
								? h(
										"ul",
										{ class: "wa-gaps" },
										gaps.value.map((g) =>
											h(
												"li",
												{ key: g.label },
												h("button", { type: "button", class: "wa-gap", onClick: () => openList(g.doctype, g.filters) }, [
													h("span", { class: "wa-gap__count" }, String(g.count)),
													h("span", { class: "wa-gap__label" }, g.label),
													h("span", { class: "wa-gap__go", innerHTML: icon("chevron-right") }),
												]),
											),
										),
								  )
								: null,
							done.value.length
								? h("p", { class: "wa-done" }, [
										h("span", { innerHTML: icon("check") }),
										gaps.value.length
											? __("All set: {0}.", [done.value.map((c, i) => (i ? c.label.toLowerCase() : c.label)).join(", ")])
											: __("Everything is published and complete."),
								  ])
								: null,
						]),

						h("section", { "aria-labelledby": "wa-giving" }, [
							h("h2", { class: "wa-heading", id: "wa-giving" }, __("Giving on the web app")),
							d.pages.length || d.campaigns.length
								? h("ul", { class: "wa-goals" }, [
										...d.pages.map((p) =>
											h("li", { key: p.name, class: "wa-goals__item" }, [
												h("button", { type: "button", class: "wa-goals__name", onClick: () => frappe.set_route("Form", "Mit Finances Donation Page", p.name) }, p.title),
												h("span", { class: "wa-goals__meta" }, p.missionary_name ? __("Gift page for {0}", [p.missionary_name]) : __("Gift page")),
												h(Goal, { raised: p.raised, goal: p.goal_amount, currency: p.currency }),
											]),
										),
										...d.campaigns.map((c) =>
											h("li", { key: c.name, class: "wa-goals__item" }, [
												h("button", { type: "button", class: "wa-goals__name", onClick: () => frappe.set_route("Form", "Mit Website Campaign", c.name) }, c.campaign_name),
												h("span", { class: "wa-goals__meta" }, c.campaign_type ? __("{0} campaign", [c.campaign_type]) : __("Campaign")),
												h(Goal, { raised: c.amount_raised, goal: c.goal_amount }),
											]),
										),
								  ])
								: h("p", { class: "wa-quiet" }, __("No gift pages or campaigns are live. Make a gift page active to show it on the web app.")),
						]),
					]),

					h("aside", { class: "wa-side" }, [
						h("section", { "aria-labelledby": "wa-apps" }, [
							h("h2", { class: "wa-heading", id: "wa-apps" }, __("Trip applications")),
							d.applications.length
								? h(
										"ul",
										{ class: "wa-feed" },
										d.applications.map((a) =>
											h(
												"li",
												{ key: a.name },
												h("button", { type: "button", class: "wa-feed__item", onClick: () => frappe.set_route("Form", "Mit Trip Application", a.name) }, [
													h("span", { class: "wa-feed__title" }, a.applicant_name || a.name),
													h("span", { class: "wa-feed__meta" }, `${a.trip}, ${day(a.application_date)}`),
													h("span", { class: "wa-feed__badge" }, a.status),
												]),
											),
										),
								  )
								: h("p", { class: "wa-quiet" }, __("No applications yet.")),
						]),
						h("section", { "aria-labelledby": "wa-gifts" }, [
							h("h2", { class: "wa-heading", id: "wa-gifts" }, __("Online gifts")),
							d.gifts.length
								? h(
										"ul",
										{ class: "wa-feed" },
										d.gifts.map((g) =>
											h(
												"li",
												{ key: g.name },
												h("button", { type: "button", class: "wa-feed__item", onClick: () => frappe.set_route("Form", "Mit Finances Donation", g.name) }, [
													h("span", { class: "wa-feed__title" }, g.supporter || __("Anonymous")),
													h("span", { class: "wa-feed__meta" }, `${g.donation_page}, ${day(g.donation_date)}`),
													h("span", { class: "wa-feed__amount" }, money(g.amount, g.currency)),
												]),
											),
										),
								  )
								: h("p", { class: "wa-quiet" }, __("No gifts through the web app yet.")),
						]),
					]),
				]),
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
