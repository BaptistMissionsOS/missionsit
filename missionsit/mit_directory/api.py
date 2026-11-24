# Copyright (c) 2026, BaptistMissionsOS and contributors
# For license information, please see license.txt

"""Map feeds — shared data, levels of disclosure.

The public map is a front door: it shows that a church or a
marketplace resource exists and where it is, and nothing more.
Full church profiles are protected: the shared data in them was
collected by missionaries' hard labor, so they are open only to
admins and to missionaries whose Directory Access Request an
admin has approved. A missionary can always open his own sending
church and church plant in full. The same rules are enforced on
the Church DocType itself (see doctype/church/church.py), so the
feeds are not the only gate. Churches and agencies reach their
own churches through the standard permission system (their role
plus a User Permission naming their church or their
organization's churches), never through these feeds.
"""

import json

import frappe
from frappe import _

from missionsit.mit_directory.doctype.mit_directory_church.mit_directory_church import (
	has_full_directory_access,
	own_church_names,
)


def _lat_lng(location):
	"""Pull (lat, lng) out of a Geolocation field's GeoJSON, or None."""
	if not location:
		return None
	try:
		data = json.loads(location) if isinstance(location, str) else location
		coords = data["features"][0]["geometry"]["coordinates"]
		return float(coords[1]), float(coords[0])
	except (ValueError, KeyError, IndexError, TypeError):
		return None


def _pins(doctype, name_field, filters=None, fields=None):
	"""Name-and-pin entries for one map layer — never more than that
	unless *fields* asks for a profile summary (missionary feed)."""
	entries = []
	for doc in frappe.get_all(
		doctype,
		filters=filters or {},
		fields=[name_field, "location"] + (fields or []),
	):
		lat_lng = _lat_lng(doc.location)
		if not lat_lng:
			continue
		entry = {"name": doc[name_field], "lat": lat_lng[0], "lng": lat_lng[1]}
		for field in fields or []:
			if field == "name":
				entry["id"] = doc["name"]
			else:
				entry[field] = doc[field]
		entries.append(entry)
	return entries


def _resource_pins(filters=None, summary=False):
	"""Marketplace listings as pins, grouped by listing type so the
	map can offer a display filter per type."""
	fields = ["name", "church", "city", "country", "status", "schedule"] if summary else []
	grouped = {}
	for listing in frappe.get_all(
		"Marketplace Listing",
		filters=filters or {},
		fields=["listing_title", "listing_type", "location"] + fields,
	):
		lat_lng = _lat_lng(listing.location)
		if not lat_lng:
			continue
		entry = {"name": listing.listing_title, "lat": lat_lng[0], "lng": lat_lng[1]}
		for field in fields:
			if field == "name":
				entry["id"] = listing["name"]
			else:
				entry[field] = listing[field]
		grouped.setdefault(listing.listing_type, []).append(entry)
	return grouped


@frappe.whitelist(allow_guest=True)
def get_public_map_pins():
	"""Public map, grouped by layer: name and pin location only.

	Only listings confirmed Active are shown; an unverified listing
	never appears on the public map.
	"""
	return {
		"churches": _pins("Church", "church_name", {"status": "Active"}),
		"resources": _resource_pins({"status": "Active"}),
	}


@frappe.whitelist()
def get_missionary_map(view="all"):
	"""Missionary map: churches and marketplace resources, grouped
	for the map's display filters.

	Admins and approved missionaries only. The view switches what
	the church layer shows: "all" (the default) is every church
	with a pin, "unverified" is churches no missionary has
	verified yet, "verified" is churches a missionary has
	confirmed, "active" is churches whose status is Active.
	Church pins carry
	their accommodation types (prophet's chamber, RV space, rooms,
	member homes) so the map can filter on those too. Resources
	return all their pins in every view, grouped by type.
	"""
	if not has_full_directory_access(frappe.session.user):
		frappe.throw(
			_("The full directory map is for admins and approved missionaries."),
			frappe.PermissionError,
		)
	if view not in ("all", "unverified", "verified", "active"):
		view = "all"
	filters = {"status": "Active"} if view == "active" else {}
	churches = _pins(
		"Church",
		"church_name",
		filters,
		fields=[
			"name",
			"status",
			"pastor_name",
			"city",
			"state_province",
			"country",
			"has_phone",
			"has_email",
			"has_website",
			"last_verified",
		],
	)
	if view == "verified":
		churches = [c for c in churches if c.get("last_verified")]
	elif view == "unverified":
		churches = [c for c in churches if not c.get("last_verified")]
	accommodations = {}
	for row in frappe.get_all(
		"Church Accommodation",
		filters={"parenttype": "Church"},
		fields=["parent", "accommodation_type"],
	):
		accommodations.setdefault(row.parent, []).append(row.accommodation_type)
	for church in churches:
		church["accommodations"] = accommodations.get(church.get("id"), [])
	return {
		"view": view,
		"churches": churches,
		"resources": _resource_pins(summary=True),
	}


@frappe.whitelist()
def get_church_profile(church):
	"""One full church profile.

	Open to admins and approved missionaries — and to any
	missionary for his own sending church or church plant.
	"""
	user = frappe.session.user
	if church in own_church_names(user) or has_full_directory_access(user):
		return frappe.get_doc("Mit Directory Church", church).as_dict()
	frappe.throw(
		_("You can view names and locations for other churches."),
		frappe.PermissionError,
	)
