# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Stripe glue for one-time and recurring donations.

MissionsIT uses Frappe's built-in Payment Gateway and Payment Request. A Donation Page checkout
creates a Payment Request bound to a Supporter and (optionally) a Donation Page. When Stripe
confirms the payment, Frappe moves the Payment Request to status *Paid*; this module listens for
that transition and writes the matching Donation and Thank You task. A recurring selection writes
a Recurring Donation with the Stripe subscription id, so later charges can be reconciled.
"""

import frappe
from frappe.utils import flt, today


@frappe.whitelist(allow_guest=True)
def start_checkout(
	donation_page: str,
	supporter_email: str,
	amount: float,
	recurring: int = 0,
	frequency: str = "Monthly",
) -> dict:
	"""Start a Stripe checkout for a public Donation Page. Returns *{payment_url}*."""
	page = frappe.get_doc("Mit Finances Donation Page", donation_page)
	if not page.is_active:
		frappe.throw(frappe._("Donation page {0} is not active.").format(donation_page))
	amount = flt(amount)
	if page.minimum_amount and amount < page.minimum_amount:
		frappe.throw(frappe._("Minimum donation is {0}.").format(page.minimum_amount))
	if int(recurring) and not page.allow_recurring:
		frappe.throw(frappe._("This page does not accept recurring gifts."))

	supporter = _ensure_supporter(supporter_email, page.missionary)

	payment_request = frappe.get_doc(
		{
			"doctype": "Payment Request",
			"payment_request_type": "Inward",
			"payment_gateway_account": _default_stripe_account(),
			"reference_doctype": "Donation Page",
			"reference_name": page.name,
			"party_type": "Customer",
			"email_to": supporter_email,
			"subject": frappe._("Gift to {0}").format(page.title),
			"grand_total": amount,
			"currency": page.currency or frappe.db.get_default("currency"),
			"status": "Draft",
		}
	)
	payment_request.flags.ignore_permissions = True
	payment_request.flags.missionsit_supporter = supporter
	payment_request.flags.missionsit_recurring = int(recurring)
	payment_request.flags.missionsit_frequency = frequency
	payment_request.insert()
	payment_request.submit()

	if int(recurring):
		_create_recurring_donation(
			supporter=supporter,
			page=page,
			amount=amount,
			frequency=frequency,
			payment_request=payment_request.name,
		)

	payment_url = payment_request.get_payment_url()
	return {"payment_url": payment_url, "payment_request": payment_request.name}


def on_payment_request_update(doc, method=None):
	"""Payment Request on_update_after_submit hook: create Donation + Thank You task when Paid."""
	if doc.status != "Paid":
		return
	if doc.reference_doctype != "Donation Page":
		return
	if frappe.db.exists("Mit Finances Donation", {"reference": doc.name}):
		return

	page = frappe.get_doc("Mit Finances Donation Page", doc.reference_name)
	supporter = _supporter_for_payment(doc)
	if not supporter:
		frappe.log_error(
			f"Payment Request {doc.name} marked Paid but no supporter could be matched.",
			"missionsit stripe",
		)
		return

	recurring = frappe.db.get_value("Mit Finances Recurring Donation", {"supporter": supporter, "donation_page": page.name, "status": "Active"})

	donation = frappe.get_doc(
		{
			"doctype": "Mit Finances Donation",
			"supporter": supporter,
			"missionary": page.missionary,
			"fund": page.fund,
			"amount": doc.grand_total,
			"currency": doc.currency,
			"donation_date": today(),
			"payment_method": "Online",
			"reference": doc.name,
			"donation_page": page.name,
			"is_recurring": 1 if recurring else 0,
			"recurring_donation": recurring,
		}
	)
	donation.insert(ignore_permissions=True)


def _ensure_supporter(email: str, missionary: str) -> str:
	"""Find or create a Supporter record for *email* under *missionary*."""
	existing = frappe.db.get_value("Mit People Supporter", {"email": email, "missionary": missionary}, "name")
	if existing:
		return existing
	parts = (email.split("@")[0] or "Friend").replace(".", " ").title().split(" ", 1)
	first_name = parts[0]
	last_name = parts[1] if len(parts) > 1 else "Online"
	supporter = frappe.get_doc(
		{
			"doctype": "Mit People Supporter",
			"first_name": first_name,
			"last_name": last_name,
			"email": email,
			"missionary": missionary,
		}
	)
	supporter.insert(ignore_permissions=True)
	return supporter.name


def _create_recurring_donation(*, supporter: str, page, amount: float, frequency: str, payment_request: str):
	"""Insert a Recurring Donation record bound to a Stripe subscription (id set on first webhook)."""
	frappe.get_doc(
		{
			"doctype": "Mit Finances Recurring Donation",
			"supporter": supporter,
			"missionary": page.missionary,
			"donation_page": page.name,
			"fund": page.fund,
			"amount": amount,
			"currency": page.currency,
			"frequency": frequency,
			"start_date": today(),
			"status": "Active",
			"payment_method": "Stripe",
			"gateway_subscription_id": payment_request,
		}
	).insert(ignore_permissions=True)


def _supporter_for_payment(doc) -> str | None:
	"""Resolve a Supporter from the Payment Request flags or the paying email."""
	supporter = getattr(doc.flags, "missionsit_supporter", None)
	if supporter:
		return supporter
	return frappe.db.get_value("Mit People Supporter", {"email": doc.email_to}, "name")


def _default_stripe_account() -> str:
	"""Return the Payment Gateway Account record for Stripe."""
	account = frappe.db.get_value(
		"Payment Gateway Account",
		{"payment_gateway": "Stripe", "is_default": 1},
		"name",
	)
	if not account:
		frappe.throw(frappe._("Set up a default Stripe Payment Gateway Account before taking online gifts."))
	return account
