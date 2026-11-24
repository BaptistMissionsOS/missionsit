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
	"Mit Finances Donation": {
		"before_insert": "missionsit.mit_finances.doctype.mit_finances_donation.mit_finances_donation.mark_first_gift",
		"after_insert": [
			"missionsit.mit_finances.doctype.mit_finances_donation.mit_finances_donation.create_thank_you_task",
			"missionsit.mit_trip.doctype.mit_trip_participant.mit_trip_participant.refresh_amount_raised",
			"missionsit.mit_website.doctype.mit_website_campaign.mit_website_campaign.refresh_amount_raised",
		],
		"on_trash": [
			"missionsit.mit_trip.doctype.mit_trip_participant.mit_trip_participant.refresh_amount_raised",
			"missionsit.mit_website.doctype.mit_website_campaign.mit_website_campaign.refresh_amount_raised",
		],
	},
	"Payment Request": {
		"on_update_after_submit": "missionsit.mit_finances.doctype.payments.stripe.on_payment_request_update",
	},
}

permission_query_conditions = {
	"Mit People Supporter": "missionsit.mit_people.doctype.mit_people_supporter.mit_people_supporter.get_permission_query_conditions",
	"Mit Finances Pledge": "missionsit.mit_finances.doctype.mit_finances_pledge.mit_finances_pledge.get_permission_query_conditions",
	"Mit Finances Donation": "missionsit.mit_finances.doctype.mit_finances_donation.mit_finances_donation.get_permission_query_conditions",
	"Mit Correspondence Ministry Task": "missionsit.mit_correspondence.doctype.mit_correspondence_ministry_task.mit_correspondence_ministry_task.get_permission_query_conditions",
	"Mit People Interaction": "missionsit.mit_people.doctype.mit_people_interaction.mit_people_interaction.get_permission_query_conditions",
	"Mit Correspondence Prayer Letter": "missionsit.mit_correspondence.doctype.mit_correspondence_prayer_letter.mit_correspondence_prayer_letter.get_permission_query_conditions",
	"Mit Directory Church": "missionsit.mit_directory.doctype.mit_directory_church.mit_directory_church.get_permission_query_conditions",
	"Mit Deputation Church Visit": "missionsit.mit_deputation.doctype.mit_deputation_church_visit.mit_deputation_church_visit.get_permission_query_conditions",
	"Mit Finances Donation Page": "missionsit.mit_finances.doctype.mit_finances_donation_page.mit_finances_donation_page.get_permission_query_conditions",
	"Mit Finances Recurring Donation": "missionsit.mit_finances.doctype.mit_finances_recurring_donation.mit_finances_recurring_donation.get_permission_query_conditions",
	"Mit People Missionary": "missionsit.mit_finances.doctype.payments.scope.missionary_permission_query",
}

has_permission = {
	"Mit People Supporter": "missionsit.mit_people.doctype.mit_people_supporter.mit_people_supporter.has_permission",
	"Mit Finances Pledge": "missionsit.mit_finances.doctype.mit_finances_pledge.mit_finances_pledge.has_permission",
	"Mit Finances Donation": "missionsit.mit_finances.doctype.mit_finances_donation.mit_finances_donation.has_permission",
	"Mit Correspondence Ministry Task": "missionsit.mit_correspondence.doctype.mit_correspondence_ministry_task.mit_correspondence_ministry_task.has_permission",
	"Mit People Interaction": "missionsit.mit_people.doctype.mit_people_interaction.mit_people_interaction.has_permission",
	"Mit Correspondence Prayer Letter": "missionsit.mit_correspondence.doctype.mit_correspondence_prayer_letter.mit_correspondence_prayer_letter.has_permission",
	"Mit Directory Church": "missionsit.mit_directory.doctype.mit_directory_church.mit_directory_church.has_permission",
	"Mit Deputation Church Visit": "missionsit.mit_deputation.doctype.mit_deputation_church_visit.mit_deputation_church_visit.has_permission",
	"Mit Finances Donation Page": "missionsit.mit_finances.doctype.mit_finances_donation_page.mit_finances_donation_page.has_permission",
	"Mit Finances Recurring Donation": "missionsit.mit_finances.doctype.mit_finances_recurring_donation.mit_finances_recurring_donation.has_permission",
}

scheduler_events = {
	"daily": [
		"missionsit.mit_finances.doctype.mit_finances_recurring_donation.mit_finances_recurring_donation.advance_due_recurring_donations",
		"missionsit.mit_correspondence.doctype.mit_correspondence_email_campaign.email_campaign_scheduler.send_due_campaigns",
	],
}
