import base64

import frappe

from event_management.event_management.doctype.event_registration.event_registration import (
	verify_signed_qr_token,
)


@frappe.whitelist(allow_guest=True)
def register_for_event(attendee, event, ticket_type, addons=None):
	if not attendee or not event or not ticket_type:
		frappe.throw("Choose an event and ticket before registering.")

	if isinstance(addons, str):
		addons = frappe.parse_json(addons)

	if addons is None:
		addons = []

	if not isinstance(addons, list):
		frappe.throw("Invalid add-on selection.")

	if not frappe.db.exists("Event Attendee", attendee):
		frappe.throw("Register your attendee details before booking an event.")

	registration = frappe.get_doc(
		{
			"doctype": "Event Registration",
			"attendee": attendee,
			"event": event,
			"ticket_type": ticket_type,
			"registration_status": "Confirmed",
			"payment_status": "Pending",
			"addons": addons,
		}
	)
	registration.insert(ignore_permissions=True)

	if not registration.qr_code:
		registration.generate_qr_image()

	return {
		"name": registration.name,
		"access_token": registration.qr_code_token,
	}


@frappe.whitelist(allow_guest=True)
def get_ticket_details(registration_name, access_token):
	if not registration_name or not access_token:
		frappe.throw("Ticket access details are missing.")

	registration = frappe.get_doc("Event Registration", registration_name)

	if (
		registration.qr_code_token != access_token
		or not verify_signed_qr_token(access_token)
	):
		frappe.throw("Invalid ticket access.")

	attendee = frappe.db.get_value(
		"Event Attendee",
		registration.attendee,
		["attendee_name", "attendee_email", "attendee_phone"],
		as_dict=True,
	)
	event_title = frappe.db.get_value(
		"Managed event",
		registration.event,
		"event_title",
	)
	ticket_name = frappe.db.get_value(
		"Event Ticket Type",
		registration.ticket_type,
		"ticket_name",
	)

	qr_file = frappe.get_all(
		"File",
		filters={
			"file_url": registration.qr_code,
			"attached_to_doctype": registration.doctype,
			"attached_to_name": registration.name,
		},
		fields=["name"],
		limit=1,
	)

	if not qr_file:
		frappe.throw("The QR ticket image is not available.")

	file_doc = frappe.get_doc("File", qr_file[0].name)
	qr_code_data = "data:image/png;base64," + base64.b64encode(
		file_doc.get_content()
	).decode("ascii")

	return {
		"name": registration.name,
		"event": event_title,
		"attendee_name": attendee.attendee_name if attendee else "",
		"attendee_email": attendee.attendee_email if attendee else "",
		"attendee_phone": attendee.attendee_phone if attendee else "",
		"ticket_type": ticket_name,
		"ticket_price": registration.ticket_price,
		"total_amount": registration.total_amount,
		"payment_status": registration.payment_status,
		"registration_status": registration.registration_status,
		"qr_code_data": qr_code_data,
	}
