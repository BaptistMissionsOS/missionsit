# This source code is freely given for the sake of the gospel (Matthew 10:8)
# and is licensed under MIT No Attribution (MIT-0).

"""Load a CSV list of churches into the Church Directory.

Put the file at missionsit/setup/data/cd.csv (or pass another path) and run:

	pilot -b church-dev frappe --site missionsit.localhost \\
		execute missionsit.setup.church_directory.import_churches

The first row names the columns, using Church field names: church_name (required),
address_line, city, state_province, postal_code, country, location, and optionally
pastor_name, phone, email, website. `location` is the GeoJSON a Geolocation field stores.

Churches are created Active, so they appear on the public map, where the web app shows only
each church's name and pin (see mit_directory/api.py get_public_map_pins). A church already in
the directory with the same name, city and state is skipped, so the import is safe to re-run.
"""

import csv
import json
import os

import frappe

DEFAULT_FILE = os.path.join(os.path.dirname(__file__), "data", "cd.csv")
FIELDS = (
	"church_name",
	"pastor_name",
	"address_line",
	"city",
	"state_province",
	"postal_code",
	"country",
	"phone",
	"email",
	"website",
	"location",
)
COMMIT_EVERY = 200


def import_churches(path: str | None = None, status: str = "Active") -> dict:
	path = path or DEFAULT_FILE
	if not os.path.exists(path):
		frappe.throw(f"No church list at {path}. Put the CSV there, or pass path=...")

	counts = {"created": 0, "skipped": 0, "no_location": 0, "errors": 0}
	countries = set(frappe.get_all("Country", pluck="name"))

	with open(path, newline="", encoding="utf-8-sig") as f:
		for line, row in enumerate(csv.DictReader(f), start=2):
			values = {k: (row.get(k) or "").strip() or None for k in FIELDS}
			if not values["church_name"]:
				counts["skipped"] += 1
				continue
			if frappe.db.exists(
				"Mit Directory Church",
				{
					"church_name": values["church_name"],
					"city": values["city"] or ["is", "not set"],
					"state_province": values["state_province"] or ["is", "not set"],
				},
			):
				counts["skipped"] += 1
				continue

			values["location"] = _point(values["location"])
			if not values["location"]:
				counts["no_location"] += 1
			if values["country"] and values["country"] not in countries:
				values["country"] = None

			try:
				frappe.get_doc(
					{
						"doctype": "Mit Directory Church",
						**values,
						"status": status,
						"data_source": os.path.basename(path),
					}
				).insert(ignore_permissions=True)
				counts["created"] += 1
			except Exception:
				counts["errors"] += 1
				frappe.log_error(title=f"Church import, line {line}: {values['church_name']}")

			if counts["created"] and counts["created"] % COMMIT_EVERY == 0:
				frappe.db.commit()

	frappe.db.commit()
	print(
		f"Created {counts['created']}, skipped {counts['skipped']} (blank or already listed), "
		f"{counts['no_location']} without a map location, {counts['errors']} errors (see Error Log)."
	)
	return counts


def _point(raw: str | None) -> str | None:
	"""The location as GeoJSON if it holds a usable point, else None."""
	if not raw:
		return None
	try:
		data = json.loads(raw)
		lng, lat = data["features"][0]["geometry"]["coordinates"][:2]
		if -90 <= float(lat) <= 90 and -180 <= float(lng) <= 180:
			return json.dumps(data, separators=(",", ":"))
	except (ValueError, KeyError, IndexError, TypeError):
		pass
	return None
