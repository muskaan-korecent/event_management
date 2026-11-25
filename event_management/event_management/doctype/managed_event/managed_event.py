
# Copyright (c) 2026, Muskaan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, get_datetime

from event_management.event_management.doctype.event_attendee.event_attendee import (
    add_attendee_details,
)


class Managedevent(Document):
    pass


@frappe.whitelist(allow_guest=True)
def get_published_events():
    events = frappe.get_all(
        "Managed event",
        filters={"event_status": "Published"},
        fields=[
            "name",
            "event_title",
            "description",
            "venue",
            "start_date",
            "start_time",
            "cover_image",
        ],
        order_by="start_date asc, start_time asc",
        limit=50,
    )
    return events


@frappe.whitelist(allow_guest=True)
def get_published_event(name):
    if not name:
        frappe.throw("Event name is required.")

    events = frappe.get_all(
        "Managed event",
        filters={"name": name, "event_status": "Published"},
        fields=[
            "name",
            "event_title",
            "description",
            "venue",
            "venue_address",
            "start_date",
            "start_time",
            "end_date",
            "end_time",
            "cover_image",
            "event_category",
            "organizer",
            "registration_deadline",
            "maximum_attendees",
        ],
        limit=1,
    )
    return events[0] if events else None


@frappe.whitelist(allow_guest=True)
def get_public_event_booking_options(name):
    if not name:
        frappe.throw("Event name is required.")

    if not frappe.db.exists(
        "Managed event",
        {"name": name, "event_status": "Published"},
    ):
        frappe.throw("This event is not available for public registration.")

    tickets = frappe.get_all(
        "Event Ticket Type",
        filters={"event": name},
        fields=[
            "name",
            "ticket_name",
            "ticket_price",
            "ticket_capacity",
            "ticket_description",
        ],
        order_by="creation asc",
        limit=100,
    )

    for ticket in tickets:
        registered_count = frappe.db.count(
            "Event Registration",
            filters={
                "ticket_type": ticket.name,
                "registration_status": ["!=", "Cancelled"],
            },
        )
        ticket.available_tickets = max(
            (ticket.ticket_capacity or 0) - registered_count,
            0,
        )

    return {
        "tickets": tickets,
        "addons": frappe.get_all(
            "Event Add-on",
            filters={"event": name},
            fields=[
                "name",
                "addon_name",
                "addon_price",
                "available_stock",
                "addon_description",
            ],
            order_by="creation asc",
            limit=100,
        ),
    }


@frappe.whitelist()
def get_organizer_dashboard():
    if frappe.session.user == "Guest":
        frappe.throw("Please log in to view the organizer dashboard.")

    current_user = frappe.session.user

  
    events = frappe.get_all(
        "Managed event",
        filters={"organizer": current_user},
        fields=["name", "event_title", "event_status"],
    )

    event_names = [event.name for event in events]

    if not event_names:
        return {
            "total_events": 0,
            "total_registrations": 0,
            "confirmed_registrations": 0,
            "checked_in": 0,
            "total_revenue": 0,
            "monthly_trends": [],
            "recent_registrations": [],
        }

    # Get registrations only for this organizer's events
    registrations = frappe.get_all(
        "Event Registration",
        filters={"event": ["in", event_names]},
        fields=[
            "name",
            "event",
            "attendee",
            "registration_status",
            "payment_status",
            "total_amount",
            "creation",
        ],
        order_by="creation desc",
    )
    add_attendee_details(registrations)

    total_registrations = len(registrations)
    confirmed = 0
    checked_in = 0
    total_revenue = 0
    monthly_data = {}

    for registration in registrations:
        if registration.registration_status == "Confirmed":
            confirmed += 1

        if registration.registration_status == "Checked In":
            checked_in += 1

        paid = registration.payment_status == "Paid"

        if paid:
            total_revenue += flt(registration.total_amount)

        month = get_datetime(registration.creation).strftime("%b %Y")

        if month not in monthly_data:
            monthly_data[month] = {
                "month": month,
                "registrations": 0,
                "revenue": 0,
            }

        monthly_data[month]["registrations"] += 1

        if paid:
            monthly_data[month]["revenue"] += flt(
                registration.total_amount
            )

    return {
        "total_events": len(events),
        "total_registrations": total_registrations,
        "confirmed_registrations": confirmed,
        "checked_in": checked_in,
        "total_revenue": total_revenue,
        "monthly_trends": list(monthly_data.values()),
        "recent_registrations": registrations[:10],
    }



@frappe.whitelist()
def get_organizer_checkin_report(event=None):
    if frappe.session.user == "Guest":
        frappe.throw("Please log in to view the check-in report.")

    current_user = frappe.session.user

    # Get events belonging to the logged-in organizer
    events = frappe.get_all(
        "Managed event",
        filters={"organizer": current_user},
        fields=["name", "event_title"],
        order_by="creation desc",
    )

    event_names = [item.name for item in events]

    if event and event not in event_names:
        frappe.throw("You are not authorized to view this event.")

    if not event_names:
        return {
            "events": [],
            "total_registrations": 0,
            "checked_in": 0,
            "not_checked_in": 0,
            "attendance_percentage": 0,
            "attendees": [],
        }

    filters = {"event": ["in", event_names]}

    if event:
        filters["event"] = event

    # Get registrations for the organizer's events
    registrations = frappe.get_all(
        "Event Registration",
        filters=filters,
        fields=[
            "name",
            "event",
            "attendee",
            "registration_status",
            "payment_status",
            "checkin_time",
        ],
        order_by="creation desc",
    )
    add_attendee_details(registrations)

    total = len(registrations)

    checked_in = sum(
        1 for item in registrations
        if item.registration_status == "Checked In"
    )

    not_checked_in = total - checked_in

    attendance_percentage = (
        round((checked_in / total) * 100, 2)
        if total else 0
    )

    return {
        "events": events,
        "total_registrations": total,
        "checked_in": checked_in,
        "not_checked_in": not_checked_in,
        "attendance_percentage": attendance_percentage,
        "attendees": registrations,
    }
