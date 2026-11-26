
# Copyright (c) 2026, Muskaan and contributors
# For license information, please see license.txt

import frappe
import secrets
import pyqrcode
import io
import hmac
import hashlib

from frappe.model.document import Document
from frappe.utils.file_manager import save_file

from event_management.event_management.doctype.event_attendee.event_attendee import (
    add_attendee_details,
)
from event_management.event_management.doctype.event_attendee.api import (
    verify_attendee_access_token,
)


# QR TOKEN SIGNING AND VERIFICATION

def get_qr_signing_key():
    encryption_key = frappe.conf.get("encryption_key")

    if not encryption_key:
        frappe.throw("Frappe encryption key is missing.")

    return encryption_key.encode("utf-8")


def create_signed_qr_token():
    random_token = secrets.token_urlsafe(32)

    signature = hmac.new(
        get_qr_signing_key(),
        random_token.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return f"{random_token}.{signature}"


def verify_signed_qr_token(token):
    if not token or not isinstance(token, str):
        return False

    try:
        random_token, received_signature = token.split(".", 1)

        if not random_token or not received_signature:
            return False

        expected_signature = hmac.new(
            get_qr_signing_key(),
            random_token.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(
            received_signature,
            expected_signature
        )

    except (ValueError, TypeError):
        return False


class EventRegistration(Document):

    def validate(self):
        self.check_event_status()
        self.check_registration_deadline()
        self.check_ticket_event()
        self.check_ticket_capacity()
        self.check_addon_event()
        self.check_addon_stock()
        self.get_ticket_price()
        self.calculate_total_amount()
        self.generate_qr_token()

    def on_update(self):
        self.generate_qr_image()

    def check_event_status(self):
        status = frappe.db.get_value(
            "Managed event", self.event, "event_status"
        )

        if status != "Published":
            frappe.throw("You can only register for published events.")

    def check_registration_deadline(self):
        deadline = frappe.db.get_value(
            "Managed event", self.event, "registration_deadline"
        )

        current_time = frappe.utils.now_datetime()

        if deadline and current_time > deadline:
            frappe.throw("The registration deadline has passed.")

    def check_ticket_event(self):
        ticket_event = frappe.db.get_value(
            "Event Ticket Type", self.ticket_type, "event"
        )

        if ticket_event != self.event:
            frappe.throw("This ticket does not belong to this event.")

    def check_ticket_capacity(self):
        if self.registration_status == "Cancelled":
            return

        capacity = frappe.db.get_value(
            "Event Ticket Type",
            self.ticket_type,
            "ticket_capacity"
        )

        if capacity is None:
            frappe.throw("Selected ticket type does not exist.")

        existing_count = frappe.db.count(
            "Event Registration",
            filters={
                "ticket_type": self.ticket_type,
                "registration_status": ["!=", "Cancelled"],
                "name": ["!=", self.name]
            }
        )

        if existing_count >= capacity:
            frappe.throw("Sorry, this ticket type is sold out.")

    def check_addon_event(self):
        for row in self.addons:
            addon_event = frappe.db.get_value(
                "Event Add-on", row.addon, "event"
            )

            if addon_event != self.event:
                frappe.throw("This add-on does not belong to this event.")

    # CHECK ADD-ON STOCK

    def check_addon_stock(self):
        addon_quantities = {}

        for row in self.addons:
            try:
                quantity = int(row.quantity)
            except (TypeError, ValueError):
                frappe.throw("Please enter a valid add-on quantity.")

            if quantity < 1:
                frappe.throw("Add-on quantity must be at least 1.")

            row.quantity = quantity

            addon_quantities[row.addon] = (
                addon_quantities.get(row.addon, 0) + quantity
            )

        for addon_name in sorted(addon_quantities):
            available_stock = frappe.db.get_value(
                "Event Add-on",
                addon_name,
                "available_stock"
            )

            if available_stock is None:
                frappe.throw("Selected add-on does not exist.")

            used_stock = frappe.get_all(
                "Event Registration Add-on",
                filters={
                    "addon": addon_name,
                    "parenttype": "Event Registration",
                    "parentfield": "addons"
                },
                fields=["parent", "quantity"]
            )

            already_used = 0

            for stock_row in used_stock:
                if stock_row.parent == self.name:
                    continue

                registration_status = frappe.db.get_value(
                    "Event Registration",
                    stock_row.parent,
                    "registration_status"
                )

                if registration_status != "Cancelled":
                    already_used += stock_row.quantity or 0

            requested_quantity = addon_quantities[addon_name]

            if already_used + requested_quantity > available_stock:
                frappe.throw(
                    "Sorry, not enough stock available for add-on: "
                    + addon_name
                )

    def get_ticket_price(self):
        self.ticket_price = frappe.db.get_value(
            "Event Ticket Type", self.ticket_type, "ticket_price"
        )

    def calculate_total_amount(self):
        addon_total = 0

        for row in self.addons:
            price = frappe.db.get_value(
                "Event Add-on", row.addon, "addon_price"
            )

            if price is None:
                frappe.throw("Invalid add-on selected.")

            quantity = row.quantity or 1

            row.amount = price * quantity
            addon_total = addon_total + row.amount

        self.addon_amount = addon_total
        self.total_amount = (self.ticket_price or 0) + addon_total

    # GENERATE SIGNED QR TOKEN

    def generate_qr_token(self):
        if self.registration_status in ["Confirmed", "Checked In"]:
            if not verify_signed_qr_token(self.qr_code_token):
                self.qr_code_token = create_signed_qr_token()

                # Regenerate QR image for the new token
                self.qr_code = None

        else:
            self.qr_code_token = None
            self.qr_code = None

    # GENERATE QR IMAGE

    def generate_qr_image(self):
        if not self.qr_code_token:
            return

        if self.qr_code:
            return

        qr = pyqrcode.create(self.qr_code_token)

        image_buffer = io.BytesIO()

        qr.png(image_buffer, scale=6)

        file_doc = save_file(
            fname="event-ticket-" + self.name + ".png",
            content=image_buffer.getvalue(),
            dt=self.doctype,
            dn=self.name,
            is_private=1,
            df="qr_code"
        )

        self.qr_code = file_doc.file_url

        self.db_set(
            "qr_code",
            file_doc.file_url,
            update_modified=False
        )


# QR CODE CHECK-IN

@frappe.whitelist()
def check_in_with_qr(token):

    if "Gate Staff" not in frappe.get_roles():
        frappe.throw("Only Gate Staff can check in attendees.")

    if not token:
        frappe.throw("QR code token is missing.")

    # Verify the signature before looking up the registration
    if not verify_signed_qr_token(token):
        frappe.throw("Invalid QR code signature.")

    registration_name = frappe.db.get_value(
        "Event Registration",
        {"qr_code_token": token},
        "name"
    )

    if not registration_name:
        frappe.throw("Invalid QR code.")

    registration = frappe.get_doc(
        "Event Registration",
        registration_name
    )

    if registration.registration_status == "Checked In":
        attendee = frappe.db.get_value(
            "Event Attendee",
            registration.attendee,
            ["attendee_name", "attendee_email"],
            as_dict=True
        )
        return {
            "success": False,
            "message": "This attendee has already been checked in.",
            "attendee_name": attendee.attendee_name if attendee else None,
            "attendee_email": attendee.attendee_email if attendee else None,
            "registration_id": registration.name,
            "event": registration.event,
            "ticket_type": registration.ticket_type,
            "payment_status": registration.payment_status,
            "registration_status": registration.registration_status,
            "checkin_time": registration.checkin_time
        }

    if registration.registration_status != "Confirmed":
        frappe.throw("This attendee is not eligible for check-in.")

    checkin_time = frappe.utils.now_datetime()

    frappe.db.set_value(
        "Event Registration",
        registration_name,
        {
            "registration_status": "Checked In",
            "checkin_time": checkin_time
        },
        update_modified=True
    )

    attendee = frappe.db.get_value(
        "Event Attendee",
        registration.attendee,
        ["attendee_name", "attendee_email"],
        as_dict=True
    )
    return {
        "success": True,
        "message": "Check-in successful!",
        "attendee_name": attendee.attendee_name if attendee else None,
        "attendee_email": attendee.attendee_email if attendee else None,
        "registration_id": registration.name,
        "event": registration.event,
        "ticket_type": registration.ticket_type,
        "payment_status": registration.payment_status,
        "registration_status": "Checked In",
        "checkin_time": checkin_time
    }


# MANUAL ATTENDEE SEARCH

@frappe.whitelist()
def search_attendees_for_checkin(search_text):

    if "Gate Staff" not in frappe.get_roles():
        frappe.throw("Only Gate Staff can search attendees.")

    if not search_text:
        frappe.throw("Please enter an attendee name or email.")

    search_text = search_text.strip()

    if len(search_text) < 2:
        frappe.throw("Please enter at least 2 characters.")

    attendees = frappe.get_all(
        "Event Attendee",
        or_filters=[
            ["attendee_name", "like", f"%{search_text}%"],
            ["attendee_email", "like", f"%{search_text}%"]
        ],
        fields=["name"],
        limit=100
    )

    attendee_names = [attendee.name for attendee in attendees]

    if not attendee_names:
        return []

    registrations = frappe.get_all(
        "Event Registration",
        filters={
            "registration_status": ["in", ["Confirmed", "Checked In"]],
            "attendee": ["in", attendee_names]
        },
        fields=[
            "name",
            "attendee",
            "registration_status",
            "payment_status",
            "event"
        ],
        limit=20
    )

    return add_attendee_details(registrations)


# MANUAL CHECK-IN

@frappe.whitelist()
def manual_checkin(registration_name):

    if "Gate Staff" not in frappe.get_roles():
        frappe.throw("Only Gate Staff can check in attendees.")

    if not registration_name:
        frappe.throw("Registration ID is missing.")

    registration = frappe.get_doc(
        "Event Registration",
        registration_name
    )

    if registration.registration_status == "Checked In":
        return "This attendee has already been checked in."

    if registration.registration_status != "Confirmed":
        frappe.throw("This attendee is not eligible for check-in.")

    frappe.db.set_value(
        "Event Registration",
        registration_name,
        {
            "registration_status": "Checked In",
            "checkin_time": frappe.utils.now_datetime()
        },
        update_modified=True
    )

    return "Check-in successful!"


@frappe.whitelist()
def get_my_registrations():

    if frappe.session.user == "Guest":
        frappe.throw("Please log in to view your registrations.")

    user_email = frappe.db.get_value(
        "User",
        frappe.session.user,
        "email"
    )

    if not user_email:
        frappe.throw("Your account does not have an email address.")

    normalized_user_email = user_email.strip().casefold()

    attendee_records = frappe.get_all(
        "Event Attendee",
        filters={"attendee_email": user_email},
        fields=["name"]
    )
    attendee_names = [attendee.name for attendee in attendee_records]

    if not attendee_names:
        return []

    registrations = frappe.get_all(
        "Event Registration",
        filters={
            "attendee": ["in", attendee_names]
        },
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
        order_by="creation desc"
    )

    registrations = add_attendee_details(registrations)
    return [
        registration
        for registration in registrations
        if (registration.attendee_email or "").strip().casefold()
        == normalized_user_email
    ]


@frappe.whitelist(allow_guest=True)
def cancel_my_registration(registration_name, attendee=None, access_token=None):
    if not registration_name:
        frappe.throw("Registration ID is missing.")

    if attendee and (
        not access_token
        or not verify_attendee_access_token(attendee, access_token)
    ):
        frappe.throw("You are not authorized to cancel this registration.")

    if not attendee and not access_token and frappe.session.user == "Guest":
        frappe.throw("Please log in to cancel your registration.")

    registration = frappe.get_doc(
        "Event Registration",
        registration_name
    )

    if attendee:
        if registration.attendee != attendee:
            attendee_email = frappe.db.get_value(
                "Event Attendee",
                attendee,
                "attendee_email",
            )
            registration_email = frappe.db.get_value(
                "Event Attendee",
                registration.attendee,
                "attendee_email",
            )
            if (
                not attendee_email
                or (registration_email or "").strip().casefold()
                != attendee_email.strip().casefold()
            ):
                frappe.throw("You are not authorized to cancel this registration.")
    elif access_token:
        if (
            registration.qr_code_token != access_token
            or not verify_signed_qr_token(access_token)
        ):
            frappe.throw("You are not authorized to cancel this registration.")
    else:
        user_email = frappe.db.get_value(
            "User",
            frappe.session.user,
            "email"
        )
        attendee_email = frappe.db.get_value(
            "Event Attendee",
            registration.attendee,
            "attendee_email"
        )

        if (
            not user_email
            or (attendee_email or "").strip().casefold()
            != user_email.strip().casefold()
        ):
            frappe.throw("You are not authorized to cancel this registration.")

    # Check current status
    if registration.registration_status == "Checked In":
        frappe.throw("A checked-in ticket cannot be cancelled.")

    if registration.registration_status == "Cancelled":
        frappe.throw("This registration is already cancelled.")

    # Get event schedule
    event = frappe.db.get_value(
        "Managed event",
        registration.event,
        ["start_date", "start_time"],
        as_dict=True
    )

    if not event or not event.start_date or not event.start_time:
        frappe.throw("Event start date or time is missing.")

    event_start = frappe.utils.get_datetime(
        f"{event.start_date} {event.start_time}"
    )

    if frappe.utils.now_datetime() >= event_start:
        frappe.throw("Registration cannot be cancelled after the event starts.")

    # Cancel registration and invalidate QR token
    frappe.db.set_value(
        "Event Registration",
        registration_name,
        {
            "registration_status": "Cancelled",
            "qr_code_token": None,
            "qr_code": None
        }
    )

    return {
        "success": True,
        "message": "Registration cancelled successfully."
    }
