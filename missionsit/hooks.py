# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

app_name = "missionsit"
app_title = "MissionsIT"
app_publisher = "MissionsIT"
app_description = "Missionary and ministry fundraising and supporter management."
app_email = "admin@missionsit.com"
app_license = "mit"

add_to_apps_screen = [
	{
		"name": "missionsit",
		"logo": "/assets/frappe/images/frappe-framework-logo.svg",
		"title": "MissionsIT",
		"route": "/desk/missionsit",
	}
]

fixtures = [
	{"dt": "Role", "filters": [["name", "in", ["Missionary", "Organization Admin", "Trip Leader"]]]},
]

after_install = "missionsit.setup.after_install"

website_route_rules = [
	{"from_route": "/donate/<slug>", "to_route": "donate"},
	{"from_route": "/apply/<trip>", "to_route": "apply"},
]

doc_events = {
	"Donation": {
		"before_insert": "missionsit.missions_donation.doctype.donation.donation.mark_first_gift",
		"after_insert": [
			"missionsit.missions_donation.doctype.donation.donation.create_thank_you_task",
			"missionsit.missions_trip_participant.doctype.trip_participant.trip_participant.refresh_amount_raised",
			"missionsit.missions_campaign.doctype.campaign.campaign.refresh_amount_raised",
		],
		"on_trash": [
			"missionsit.missions_trip_participant.doctype.trip_participant.trip_participant.refresh_amount_raised",
			"missionsit.missions_campaign.doctype.campaign.campaign.refresh_amount_raised",
		],
	},
	"Payment Request": {
		"on_update_after_submit": "missionsit.missions_payments.stripe.on_payment_request_update",
	},
}

permission_query_conditions = {
	"Supporter": "missionsit.missions_supporter.doctype.supporter.supporter.get_permission_query_conditions",
	"Pledge": "missionsit.missions_pledge.doctype.pledge.pledge.get_permission_query_conditions",
	"Donation": "missionsit.missions_donation.doctype.donation.donation.get_permission_query_conditions",
	"Ministry Task": "missionsit.missions_ministry_task.doctype.ministry_task.ministry_task.get_permission_query_conditions",
	"Interaction": "missionsit.missions_interaction.doctype.interaction.interaction.get_permission_query_conditions",
	"Prayer Letter": "missionsit.missions_prayer_letter.doctype.prayer_letter.prayer_letter.get_permission_query_conditions",
	"Church Visit": "missionsit.missions_church_visit.doctype.church_visit.church_visit.get_permission_query_conditions",
	"Donation Page": "missionsit.missions_donation_page.doctype.donation_page.donation_page.get_permission_query_conditions",
	"Recurring Donation": "missionsit.missions_recurring_donation.doctype.recurring_donation.recurring_donation.get_permission_query_conditions",
	"Missionary": "missionsit.missions_payments.scope.missionary_permission_query",
}

has_permission = {
	"Supporter": "missionsit.missions_supporter.doctype.supporter.supporter.has_permission",
	"Pledge": "missionsit.missions_pledge.doctype.pledge.pledge.has_permission",
	"Donation": "missionsit.missions_donation.doctype.donation.donation.has_permission",
	"Ministry Task": "missionsit.missions_ministry_task.doctype.ministry_task.ministry_task.has_permission",
	"Interaction": "missionsit.missions_interaction.doctype.interaction.interaction.has_permission",
	"Prayer Letter": "missionsit.missions_prayer_letter.doctype.prayer_letter.prayer_letter.has_permission",
	"Church Visit": "missionsit.missions_church_visit.doctype.church_visit.church_visit.has_permission",
	"Donation Page": "missionsit.missions_donation_page.doctype.donation_page.donation_page.has_permission",
	"Recurring Donation": "missionsit.missions_recurring_donation.doctype.recurring_donation.recurring_donation.has_permission",
}

scheduler_events = {
	"daily": [
		"missionsit.missions_recurring_donation.doctype.recurring_donation.recurring_donation.advance_due_recurring_donations",
		"missionsit.missions_ministry_task.automation.create_birthday_tasks",
		"missionsit.missions_ministry_task.automation.create_anniversary_tasks",
		"missionsit.missions_ministry_task.automation.create_lapsed_donor_tasks",
		"missionsit.missions_email_campaign.doctype.email_campaign.email_campaign_scheduler.send_due_campaigns",
	],
}
