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
		"route": "/desk/summary",
	}
]

fixtures = [
	{"dt": "Role", "filters": [["name", "in", ["Missionary", "Organization Admin", "Trip Leader", "Church User", "Agency User"]]]},
]

after_install = "missionsit.setup.after_install"

website_route_rules = [
	{"from_route": "/donate/<slug>", "to_route": "donate"},
	{"from_route": "/apply/<trip>", "to_route": "apply"},
]

doc_events = {
	"Donation": {
		"before_insert": "missionsit.missions_finances.doctype.donation.donation.mark_first_gift",
		"after_insert": [
			"missionsit.missions_finances.doctype.donation.donation.create_thank_you_task",
			"missionsit.missions_trip.doctype.trip_participant.trip_participant.refresh_amount_raised",
			"missionsit.mit_website.doctype.mit_website_campaign.mit_website_campaign.refresh_amount_raised",
		],
		"on_trash": [
			"missionsit.missions_trip.doctype.trip_participant.trip_participant.refresh_amount_raised",
			"missionsit.mit_website.doctype.mit_website_campaign.mit_website_campaign.refresh_amount_raised",
		],
	},
	"Payment Request": {
		"on_update_after_submit": "missionsit.missions_finances.doctype.payments.stripe.on_payment_request_update",
	},
}

permission_query_conditions = {
	"Supporter": "missionsit.missions_people.doctype.supporter.supporter.get_permission_query_conditions",
	"Pledge": "missionsit.missions_finances.doctype.pledge.pledge.get_permission_query_conditions",
	"Donation": "missionsit.missions_finances.doctype.donation.donation.get_permission_query_conditions",
	"Ministry Task": "missionsit.missions_correspondence.doctype.ministry_task.ministry_task.get_permission_query_conditions",
	"Interaction": "missionsit.missions_people.doctype.interaction.interaction.get_permission_query_conditions",
	"Prayer Letter": "missionsit.missions_correspondence.doctype.prayer_letter.prayer_letter.get_permission_query_conditions",
	"Church": "missionsit.missions_directory.doctype.church.church.get_permission_query_conditions",
	"Church Visit": "missionsit.missions_deputation.doctype.church_visit.church_visit.get_permission_query_conditions",
	"Donation Page": "missionsit.missions_finances.doctype.donation_page.donation_page.get_permission_query_conditions",
	"Recurring Donation": "missionsit.missions_finances.doctype.recurring_donation.recurring_donation.get_permission_query_conditions",
	"Missions Missionary": "missionsit.missions_finances.doctype.payments.scope.missionary_permission_query",
}

has_permission = {
	"Supporter": "missionsit.missions_people.doctype.supporter.supporter.has_permission",
	"Pledge": "missionsit.missions_finances.doctype.pledge.pledge.has_permission",
	"Donation": "missionsit.missions_finances.doctype.donation.donation.has_permission",
	"Ministry Task": "missionsit.missions_correspondence.doctype.ministry_task.ministry_task.has_permission",
	"Interaction": "missionsit.missions_people.doctype.interaction.interaction.has_permission",
	"Prayer Letter": "missionsit.missions_correspondence.doctype.prayer_letter.prayer_letter.has_permission",
	"Church": "missionsit.missions_directory.doctype.church.church.has_permission",
	"Church Visit": "missionsit.missions_deputation.doctype.church_visit.church_visit.has_permission",
	"Donation Page": "missionsit.missions_finances.doctype.donation_page.donation_page.has_permission",
	"Recurring Donation": "missionsit.missions_finances.doctype.recurring_donation.recurring_donation.has_permission",
}

scheduler_events = {
	"daily": [
		"missionsit.missions_finances.doctype.recurring_donation.recurring_donation.advance_due_recurring_donations",
		"missionsit.missions_correspondence.doctype.email_campaign.email_campaign_scheduler.send_due_campaigns",
	],
}
