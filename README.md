# MissionSit

A free, focused CRM and fundraising app for missionaries and sending organizations, built on Frappe Framework v16.

## What it does

One missionary manages their supporters from first contact through active partnership: tracking partnership stages, recording pledges and donations, creating follow-up tasks, logging interactions, sending prayer letters, running online donation pages, recruiting for short-term trips, and visiting supporting churches.

## DocTypes

Every DocType is namespaced under its module (`Mit <Module> <Name>`) so no DocType or module name can shadow another app.

### People and giving

| DocType | Purpose |
|---|---|
| **Mit People Organization** | Sending churches, agencies and mission boards |
| **Mit People Missionary** | The central profile for each missionary |
| **Mit People Supporter** | Individuals and families who partner with a missionary |
| **Mit Deputation Partnership Stage** | Funnel stages (Contact, Appointment, Presentation, Partner, Lapsed) |
| **Mit People Supporter Group** | Named lists of supporters for targeted communication |
| **Mit People Supporter Referral** | Tracks who referred a supporter to the missionary |
| **Mit Finances Fund** | Named buckets for donations (General Support, Project funds) |
| **Mit Finances Pledge** | A commitment to give at a set amount and frequency |
| **Mit Finances Donation** | A recorded gift from a supporter |
| **Mit Finances Recurring Donation** | A scheduled gift that renews on a frequency |

### Online giving

| DocType | Purpose |
|---|---|
| **Mit Finances Donation Page** | A public /donate/<slug> page with Stripe checkout |
| **Mit Website Campaign** | A themed giving drive (peer-to-peer, special project, matching) |
| **Mit Correspondence Email Campaign** | A supporter-group email broadcast with scheduled send |

### Trips

| DocType | Purpose |
|---|---|
| **Mit Trip** | A short-term missions trip with destination, dates, and cost |
| **Mit Trip Application** | A public application submitted at /apply/<trip> |
| **Mit Trip Participant** | An accepted traveler with support-raising progress |

### Churches

| DocType | Purpose |
|---|---|
| **Mit Directory Church** | A supporting or prospective church |
| **Mit Deputation Church Visit** | A scheduled or completed visit to a church |

### Activity

| DocType | Purpose |
|---|---|
| **Mit Correspondence Ministry Task** | Action items: thank-you notes, calls, visits, follow-ups |
| **Mit People Interaction** | A logged touchpoint: call, email, meeting, gift |
| **Mit Correspondence Prayer Letter** | Newsletters and update letters sent to supporters |

## Public pages

| URL | Purpose |
|---|---|
| `/donate/<slug>` | Public donation form, posts to Stripe checkout |
| `/apply/<trip>` | Public trip application form |

## Automatic actions

- **Mit Finances Donation after insert** creates a thank-you Mit Correspondence Ministry Task, links it to the Supporter, and updates any linked Mit Finances Pledge balance.
- **Mit Trip Application set to Accepted** promotes the applicant to a Mit Trip Participant.
- **Daily scheduler** advances Mit Finances Recurring Donations whose next_payment_date is due, and creates Ministry Tasks for upcoming birthdays, partnership anniversaries, and lapsed donors (no gift in the last 90 days).
- **Mit Correspondence Email Campaign set to Scheduled** sends when its scheduled_date is reached.
- **Payment Request paid** creates a Mit Finances Donation and, if recurring, a Mit Finances Recurring Donation record with the gateway subscription id.

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
| **Missionary** | Read and write only the records linked to their own Mit People Missionary record |
| **Organization Admin** | Read and write Mit People Missionary and Mit Finances Donation records inside the organizations they administer |
| **Trip Leader** | Read and write Mit Trip, Mit Trip Application, and Mit Trip Participant records |

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
