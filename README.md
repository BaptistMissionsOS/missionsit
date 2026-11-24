<div align="center">

# MissionsIT

**A fully open-source CRM and fundraising app for missionaries and sending organizations, built on the [Frappe Framework](https://frappe.io/framework).**

[![GitHub License](https://img.shields.io/github/license/BaptistMissionsOS/missionsit)](https://github.com/BaptistMissionsOS/missionsit?tab=readme-ov-file#-license-mit-0)
![GitHub contributors](https://img.shields.io/github/contributors/BaptistMissionsOS/missionsit)
![GitHub last commit](https://img.shields.io/github/last-commit/BaptistMissionsOS/missionsit)

[Features](#-features) · [Install](#-installing-missionsit) · [Contributing](#-contributing) · [Get help](https://github.com/BaptistMissionsOS/missionsit/issues)

</div>

> [!NOTE]
> **This project is looking for additional developers!** If you are interested in contributing, please [open an issue on GitHub](https://github.com/BaptistMissionsOS/missionsit/issues/new).

## ✨ Features

One missionary manages their supporters from first contact through active partnership: tracking partnership stages, recording pledges and donations, creating follow-up tasks, logging interactions, sending prayer letters, running online donation pages, recruiting for short-term trips, and visiting supporting churches.

Every DocType is namespaced under its module (`Mit <Module> <Name>`) so no DocType or module name can shadow another app.

### People & giving

- **Mit People Organization** — Sending churches, agencies and mission boards
- **Mit People Missionary** — The central profile for each missionary
- **Mit People Supporter** — Individuals and families who partner with a missionary
- **Mit Deputation Partnership Stage** — Funnel stages (Contact, Appointment, Presentation, Partner, Lapsed)
- **Mit People Supporter Group** — Named lists of supporters for targeted communication
- **Mit People Supporter Referral** — Tracks who referred a supporter to the missionary
- **Mit Finances Fund** — Named buckets for donations (General Support, Project funds)
- **Mit Finances Pledge** — A commitment to give at a set amount and frequency
- **Mit Finances Donation** — A recorded gift from a supporter
- **Mit Finances Recurring Donation** — A scheduled gift that renews on a frequency

### Online giving

- **Mit Finances Donation Page** — A public `/donate/<slug>` page with Stripe checkout
- **Mit Website Campaign** — A themed giving drive (peer-to-peer, special project, matching)
- **Mit Correspondence Email Campaign** — A supporter-group email broadcast with scheduled send

### Trips

- **Mit Trip** — A short-term missions trip with destination, dates, and cost
- **Mit Trip Application** — A public application submitted at `/apply/<trip>`
- **Mit Trip Participant** — An accepted traveler with support-raising progress

### Churches

- **Mit Directory Church** — A supporting or prospective church (shared directory)
- **Mit Deputation Church Visit** — A scheduled or completed visit to a church

### Activity

- **Mit Correspondence Ministry Task** — Action items: thank-you notes, calls, visits, follow-ups
- **Mit People Interaction** — A logged touchpoint: call, email, meeting, gift
- **Mit Correspondence Prayer Letter** — Newsletters and update letters sent to supporters

### Public pages

- `/donate/<slug>` — Public donation form, posts to Stripe checkout
- `/apply/<trip>` — Public trip application form

### Automatic actions

- **Donation after insert** creates a thank-you Ministry Task, links it to the Supporter, and updates any linked Pledge balance.
- **Trip Application set to Accepted** promotes the applicant to a Trip Participant.
- **Daily scheduler** advances Recurring Donations whose `next_payment_date` is due, and creates Ministry Tasks for upcoming birthdays, partnership anniversaries, and lapsed donors (no gift in the last 90 days).
- **Email Campaign set to Scheduled** sends when its `scheduled_date` is reached.
- **Payment Request paid** creates a Donation and, if recurring, a Recurring Donation record with the gateway subscription id.

### Roles

| Role | Access |
|---|---|
| **System Manager** | Full access to all records |
| **Missionary** | Read and write only the records linked to their own Mit People Missionary record |
| **Organization Admin** | Read and write Mit People Missionary and Mit Finances Donation records inside the organizations they administer |
| **Trip Leader** | Read and write Mit Trip, Mit Trip Application, and Mit Trip Participant records |

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
