import frappe
from frappe.model.document import Document


class EventAttendee(Document):
	pass


def add_attendee_details(registrations):
	attendee_names = {row.attendee for row in registrations if row.get("attendee")}

	if not attendee_names:
		for row in registrations:
			row.attendee_name = None
			row.attendee_email = None
			row.attendee_phone = None
		return registrations

	attendees = frappe.get_all(
		"Event Attendee",
		filters={"name": ["in", list(attendee_names)]},
		fields=["name", "attendee_name", "attendee_email", "attendee_phone"],
	)
	attendees_by_name = {attendee.name: attendee for attendee in attendees}

	for row in registrations:
		attendee = attendees_by_name.get(row.get("attendee"))
		row.attendee_name = attendee.attendee_name if attendee else None
		row.attendee_email = attendee.attendee_email if attendee else None
		row.attendee_phone = attendee.attendee_phone if attendee else None

	return registrations
