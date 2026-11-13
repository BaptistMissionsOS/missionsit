# MissionSit

A free, focused CRM and fundraising app for missionaries and sending organizations, built on Frappe Framework v16.

## What it does

One missionary manages their supporters from first contact through active partnership: tracking partnership stages, recording pledges and donations, creating follow-up tasks, logging interactions, sending prayer letters, running online donation pages, recruiting for short-term trips, and visiting supporting churches.

## DocTypes

### People and giving

| DocType | Purpose |
|---|---|
| **Organization** | Sending churches, agencies and mission boards |
| **Missionary** | The central profile for each missionary |
| **Supporter** | Individuals and families who partner with a missionary |
| **Partnership Stage** | Funnel stages (Contact, Appointment, Presentation, Partner, Lapsed) |
| **Supporter Group** | Named lists of supporters for targeted communication |
| **Supporter Referral** | Tracks who referred a supporter to the missionary |
| **Fund** | Named buckets for donations (General Support, Project funds) |
| **Pledge** | A commitment to give at a set amount and frequency |
| **Donation** | A recorded gift from a supporter |
| **Recurring Donation** | A scheduled gift that renews on a frequency |

### Online giving

| DocType | Purpose |
|---|---|
| **Donation Page** | A public /donate/<slug> page with Stripe checkout |
| **Campaign** | A themed giving drive (peer-to-peer, special project, matching) |
| **Email Campaign** | A supporter-group email broadcast with scheduled send |

### Trips

| DocType | Purpose |
|---|---|
| **Trip** | A short-term missions trip with destination, dates, and cost |
| **Trip Application** | A public application submitted at /apply/<trip> |
| **Trip Participant** | An accepted traveler with support-raising progress |

### Churches

| DocType | Purpose |
|---|---|
| **Church** | A supporting or prospective church |
| **Church Visit** | A scheduled or completed visit to a church |

### Activity

| DocType | Purpose |
|---|---|
| **Ministry Task** | Action items: thank-you notes, calls, visits, follow-ups |
| **Interaction** | A logged touchpoint: call, email, meeting, gift |
| **Prayer Letter** | Newsletters and update letters sent to supporters |

## Public pages

| URL | Purpose |
|---|---|
| `/donate/<slug>` | Public donation form, posts to Stripe checkout |
| `/apply/<trip>` | Public trip application form |

## Automatic actions

- **Donation after insert** creates a thank-you Ministry Task, links it to the Supporter, and updates any linked Pledge balance.
- **Trip Application set to Accepted** promotes the applicant to a Trip Participant.
- **Daily scheduler** advances Recurring Donations whose next_payment_date is due, and creates Ministry Tasks for upcoming birthdays, partnership anniversaries, and lapsed donors (no gift in the last 90 days).
- **Email Campaign set to Scheduled** sends when its scheduled_date is reached.
- **Payment Request paid** creates a Donation and, if recurring, a Recurring Donation record with the gateway subscription id.

## Installation

```bash
cd /path/to/bench
bench get-app https://github.com/your-org/missionsit
bench --site your-site.localhost install-app missionsit
bench --site your-site.localhost migrate
```

Or, if the app is already in your bench's `apps/` folder:

```bash
bench --site your-site.localhost install-app missionsit
bench --site your-site.localhost migrate
```

## Stripe setup

1. Open **Payment Gateway Account** and create one with `payment_gateway` set to **Stripe**, `is_default` checked, and your Stripe keys.
2. Create a **Donation Page**, set a slug, pick the missionary and fund, and tick **Allow recurring** if you want monthly gifts.
3. Share the public link `/donate/<slug>`.

## Roles

| Role | Access |
|---|---|
| **System Manager** | Full access to all records |
| **Missionary** | Read and write only the records linked to their own Missionary record |
| **Organization Admin** | Read and write Missionary and Donation records inside the organizations they administer |
| **Trip Leader** | Read and write Trip, Trip Application, and Trip Participant records |

## Before you open a pull request

Run `pre-commit install` once after cloning, then before every commit:

```bash
pre-commit run --files <changed files>
```

Run the test suite on a test site (not a site with data you need):

```bash
bench --site test.localhost run-tests --app missionsit
```

## AI Policy

Pull requests that contain only AI-generated code with no personal input from the contributor will be delayed or rejected. Describe the problem you are solving in your own words in the pull request body.
