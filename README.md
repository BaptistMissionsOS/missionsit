<div align="center">

# MissionsIT

**A fully open-source missions management system, built on the [Frappe Framework](https://frappe.io/framework).**

[![GitHub License](https://img.shields.io/github/license/BaptistMissionsOS/missionsit)](https://github.com/BaptistMissionsOS/missionsit?tab=readme-ov-file#-license-mit-0)
![GitHub contributors](https://img.shields.io/github/contributors/BaptistMissionsOS/missionsit)
![GitHub last commit](https://img.shields.io/github/last-commit/BaptistMissionsOS/missionsit)

[Features](#-features) · [Install](#-installing-missionsit) · [Contributing](#-contributing) · [Get help](https://github.com/BaptistMissionsOS/missionsit/issues)

</div>

> [!NOTE]
> **This project is looking for additional developers!** If you are interested in contributing, please [open an issue on GitHub](https://github.com/BaptistMissionsOS/missionsit/issues/new).

## ✨ Features

### Supporters & giving
- One missionary manages supporters from first contact through active partnership, moving them through a partnership funnel (Contact, Appointment, Presentation, Partner, Lapsed) that each sending organization can customize
- Pledges track each supporter's commitment and frequency, and the pledge progress chart compares pledged amounts against gifts received
- Donations allocate to named funds (General Support, project funds), roll up to the missionary, and credit any linked pledge automatically
- Recurring donations advance on their due date through a daily scheduler and record the gateway subscription when they renew
- Automatic thank-you task on every donation, linked back to the supporter, so no gift goes unacknowledged
- Supporter groups for targeted outreach (year-end appeal, prayer team, major donors), and a supporter referral trail so a missionary can thank the person who introduced each new partner
- Birthday, partnership anniversary and lapsed-donor (no gift in 90 days) ministry tasks created each morning so follow-up stays on the calendar
- Interactions timeline on each supporter — calls, emails, meetings, gifts — so anyone looking at the record sees the whole relationship

### Online giving
- Stripe checkout donation pages with a fund picker and an optional recurring-gift toggle
- Payment Request paid creates the Donation (and the Recurring Donation on renewals) itself, with the gateway subscription id for later changes
- Themed campaigns (peer-to-peer, special project, matching) with their own goal and running total
- Publishable missionary profile pages with a headline, photo, field summary and bio
- A member portal with signups, donations and trip applications that each sending organization can turn on

### Trips
- Short-term trip planning: destination, dates, per-person cost and status
- Public applications flow into the desk; accepting an application promotes the applicant to a Trip Participant automatically
- Each participant's support-raising progress rolls up from their linked donations, so trip leaders see who is fully funded at a glance
- Trip expenses tracked per trip

### Deputation & churches
- Shared Church directory with submissions and verifications, so church profiles are kept up to date by the people who know them
- Access requests when a missionary wants to use the directory
- Church visits: scheduled and completed, with the missionary, date, and outcome
- Deputation schedule: plan a region or itinerary with a target number of churches between two dates
- Reusable presentations (slides, videos, printed material) attached to visits

### Correspondence
- Prayer letters written in the desk and sent to supporter groups
- Email campaigns with a scheduled send date; the daily scheduler sends each campaign when its date is reached
- Correspondence log: a single record of every letter, email and message sent, filterable per supporter
- Ministry tasks (thank-you notes, calls, visits, follow-ups) as a to-do list with due dates and owners

### Prayer
- Prayer requests from a missionary, with a category and a status so answered prayer can be marked
- Prayer teams built from supporters; a request can be shared with the team or kept private
- Prayer updates post progress and answers to the people praying

### Missionary life
- Furlough tracking: start and end dates, home base, additional monthly support target, and goals for the time home
- Tentmaker jobs: part-time or full-time work a missionary takes abroad, with employer, country, hours, and whether the job provides a visa
- Business contacts and skills/services for tentmaker missionaries
- Ministry projects and activities so a missionary can report what the funds are accomplishing on the field, with linked ministry partners

### Marketplace
- Listings posted by churches, organizations and missionaries — ministry opportunities, resources, short-term housing — with map location and host church

### Finances
- Funds, pledges, donations and recurring donations tied together so a pledge's balance updates whenever a gift comes in
- Expense tracking by category and financial period
- Budgets and a general ledger view for the missionary's own bookkeeping

### Automatic actions
- A donation creates a thank-you task and credits any linked pledge
- An accepted trip application promotes the applicant to a trip participant
- A paid payment request records a donation (and a recurring donation on renewals) by itself
- The daily scheduler advances recurring donations that are due, sends scheduled email campaigns, and creates follow-up tasks for birthdays, partnership anniversaries and lapsed donors

## 📥 Installing MissionsIT

There are two ways to run MissionsIT. Pick the one that fits you:

|                                                               | Best for                                                                  | Cost  | Effort         |
| ------------------------------------------------------------- | ------------------------------------------------------------------------- | ----- | -------------- |
| [Existing Frappe bench (Pilot)](#existing-frappe-bench-pilot) | Admins who already run Frappe, or want other Frappe apps alongside MissionsIT | Free  | A few commands |
| [Plain `bench`](#plain-bench)                                 | Any Frappe bench without Pilot                                            | Free  | A few commands |

### Existing Frappe bench (Pilot)

[Pilot](https://github.com/frappe/pilot) is Frappe's official tool for running benches on your own Linux server. Follow Pilot's README to install it and create a bench, then:

```bash
# Replace "church" with your bench name and missions.example.org with your domain.
pilot -b church get-app https://github.com/BaptistMissionsOS/missionsit --install-dependencies
pilot -b church new-site missions.example.org --apps missionsit
pilot -b church setup production
```

**To update:** `pilot -b church update`.

### Plain `bench`

```bash
cd /path/to/bench
bench get-app https://github.com/BaptistMissionsOS/missionsit
bench --site your-site.localhost install-app missionsit
bench --site your-site.localhost migrate
```

## ⚙️ Stripe setup

1. Open **Payment Gateway Account** and create one with `payment_gateway` set to **Stripe**, `is_default` checked, and your Stripe keys.
2. Create a **Mit Finances Donation Page**, set a slug, pick the missionary and fund, and tick **Allow recurring** if you want monthly gifts.
3. Share the public link `/donate/<slug>`.

## 🆘 Support

If you need help setting up the app or configuring it, [open an issue on GitHub](https://github.com/BaptistMissionsOS/missionsit/issues).

## 🤖 AI Policy

Pull requests that contain only AI-generated code with no personal input from the contributor will be delayed or rejected. Describe the problem you are solving in your own words in the pull request body.

## 🤝 Contributing

Contributions are very welcome! If you plan any large contributions, please open an issue first so we can coordinate.

### Before you open a pull request

Run `pre-commit install` once after cloning, then before every commit:

```bash
pre-commit run --files <changed files>
```

Run the test suite on a test site (not a site with data you need):

```bash
bench --site test.localhost run-tests --app missionsit
```

### DocType naming

Every app DocType is prefixed with its module (`Mit <Module> <Name>`), matching the convention used by `mit_website`. This keeps MissionsIT from shadowing a DocType owned by another app, and makes it clear from any DocType name which module owns it. When you add a new DocType, follow the same pattern.

### Managing app data

**Fixtures** (`hooks.py` → `fixtures`) are app-owned data re-applied on every `bench migrate`. The current fixtures are the custom **Role** records.

**After-install data** (`missionsit/setup.py` → `after_install`) is user-owned starter data applied once on new installs only. Users can modify or delete it freely; it will not be recreated on migration.

**Patches** (`patches.txt`) are versioned, one-time data migrations. Append to `patches.txt`, never insert above existing entries.

## 🔑 License: MIT-0

```
MIT No Attribution

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

`This resource is freely given (Matt 10:8) for the sake of the gospel`
