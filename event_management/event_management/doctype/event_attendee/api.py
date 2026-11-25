import hashlib
import hmac

import frappe

from event_management.event_management.doctype.event_attendee.event_attendee import (
	add_attendee_details,
)


def _attendee_access_key():
	encryption_key = frappe.conf.get("encryption_key")
	if not encryption_key:
		frappe.throw("Frappe encryption key is missing.")
	return encryption_key.encode("utf-8")


def create_attendee_access_token(attendee_name):
	signature = hmac.new(
		_attendee_access_key(),
		attendee_name.encode("utf-8"),
		hashlib.sha256,
	).hexdigest()
	return f"{attendee_name}.{signature}"


def verify_attendee_access_token(attendee_name, access_token):
	if not attendee_name or not isinstance(access_token, str):
		return False

	try:
		token_attendee, signature = access_token.rsplit(".", 1)
	except ValueError:
		return False

	if token_attendee != attendee_name or not signature:
		return False

	expected_signature = hmac.new(
		_attendee_access_key(),
		attendee_name.encode("utf-8"),
		hashlib.sha256,
	).hexdigest()

	return hmac.compare_digest(signature, expected_signature)


def _attendee_session(attendee):
	return {
		"name": attendee.name,
		"access_token": create_attendee_access_token(attendee.name),
		"attendee_name": attendee.attendee_name,
		"attendee_email": attendee.attendee_email,
		"attendee_phone": attendee.attendee_phone,
	}


@frappe.whitelist(allow_guest=True)
def register_attendee(attendee_name, attendee_email, attendee_phone):
	attendee_name = (attendee_name or "").strip()
	attendee_email = (attendee_email or "").strip()
	attendee_phone = (attendee_phone or "").strip()

	if not attendee_name:
		frappe.throw("Please enter your name.")

	if not attendee_email:
		frappe.throw("Please enter your email address.")

	if not attendee_phone:
		frappe.throw("Please enter your phone number.")

	existing_attendees = frappe.get_all(
		"Event Attendee",
		filters={"attendee_email": attendee_email},
		fields=["name"],
		order_by="creation asc",
		limit_page_length=1,
	)
	if existing_attendees:
		return {"already_registered": True}

	attendee = frappe.get_doc(
		{
			"doctype": "Event Attendee",
			"attendee_name": attendee_name,
			"attendee_email": attendee_email,
			"attendee_phone": attendee_phone,
		}
	)
	attendee.insert(ignore_permissions=True)

	return _attendee_session(attendee)


@frappe.whitelist(allow_guest=True)
def get_attendee_registrations(attendee, access_token):
	if not attendee or not access_token:
		frappe.throw("Attendee access details are missing.")

	if not verify_attendee_access_token(attendee, access_token):
		frappe.throw("Invalid attendee access.")

	if not frappe.db.exists("Event Attendee", attendee):
		frappe.throw("Attendee was not found.")

	attendee_email = frappe.db.get_value(
		"Event Attendee",
		attendee,
		"attendee_email",
	)
	attendee_records = frappe.get_all(
		"Event Attendee",
		filters={"attendee_email": attendee_email},
		fields=["name"],
	)
	attendee_names = [record.name for record in attendee_records]

	registrations = frappe.get_all(
		"Event Registration",
		filters={"attendee": ["in", attendee_names]},
		fields=[
			"name",
			"event",
			"attendee",
			"ticket_type",
			"registration_status",
			"payment_status",
			"total_amount",
			"creation",
			"qr_code",
			"qr_code_token",
		],
		order_by="creation desc",
	)

	return add_attendee_details(registrations)
