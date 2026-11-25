
# Copyright (c) 2026, Muskaan and Contributors
# See license.txt

from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase

from event_management.event_management.doctype.event_attendee.api import (
    create_attendee_access_token,
    get_attendee_registrations,
    register_attendee,
    verify_attendee_access_token,
)
from event_management.event_management.doctype.event_registration.event_registration import (
    check_in_with_qr,
    cancel_my_registration,
    create_signed_qr_token,
    get_my_registrations,
    verify_signed_qr_token,
)


class IntegrationTestEventRegistration(IntegrationTestCase):

    def test_qr_token_generated_for_paid_confirmed_registration(self):
        registration = frappe.get_doc({
            "doctype": "Event Registration",
            "payment_status": "Paid",
            "registration_status": "Confirmed"
        })

        registration.generate_qr_token()

        self.assertTrue(registration.qr_code_token)
        self.assertTrue(verify_signed_qr_token(registration.qr_code_token))

    def test_qr_token_not_generated_for_pending_registration(self):
        registration = frappe.get_doc({
            "doctype": "Event Registration",
            "payment_status": "Paid",
            "registration_status": "Pending"
        })

        registration.generate_qr_token()

        self.assertIsNone(registration.qr_code_token)

    def test_qr_token_generated_for_confirmed_pending_payment_registration(self):
        registration = frappe.get_doc({
            "doctype": "Event Registration",
            "payment_status": "Pending",
            "registration_status": "Confirmed"
        })

        registration.generate_qr_token()

        self.assertTrue(registration.qr_code_token)
        self.assertTrue(verify_signed_qr_token(registration.qr_code_token))

    def test_existing_qr_token_is_not_changed(self):
        existing_token = create_signed_qr_token()

        registration = frappe.get_doc({
            "doctype": "Event Registration",
            "payment_status": "Paid",
            "registration_status": "Confirmed",
            "qr_code_token": existing_token
        })

        registration.generate_qr_token()

        self.assertEqual(
            registration.qr_code_token,
            existing_token
        )

    def test_invalid_qr_token_signature_is_rejected(self):
        token = create_signed_qr_token()
        tampered_token = token[:-1] + (
            "0" if token[-1] != "0" else "1"
        )

        self.assertFalse(verify_signed_qr_token(tampered_token))

    def test_ticket_capacity_prevents_overselling(self):
        registration = frappe.get_doc({
            "doctype": "Event Registration",
            "name": "TEST-REGISTRATION-2",
            "ticket_type": "TEST-TICKET",
            "registration_status": "Pending"
        })

        with patch.object(
            frappe.db,
            "get_value",
            return_value=1
        ), patch.object(
            frappe.db,
            "count",
            return_value=1
        ):
            with self.assertRaises(frappe.ValidationError):
                registration.check_ticket_capacity()

    def test_addon_stock_prevents_overselling(self):
        registration = frappe.get_doc({
            "doctype": "Event Registration",
            "name": "TEST-ADDON-REGISTRATION",
            "addons": [
                {
                    "addon": "TEST-ADDON",
                    "quantity": 2
                }
            ]
        })

        mock_stock_rows = [
            frappe._dict(parent="REG-1", quantity=3),
            frappe._dict(parent="REG-2", quantity=1),
        ]

        with patch.object(
            frappe.db, "get_value", side_effect=[5, "Confirmed", "Confirmed"]
        ), patch.object(
            frappe, "get_all", return_value=mock_stock_rows
        ):
            with self.assertRaises(frappe.ValidationError):
                registration.check_addon_stock()

    def test_non_gate_staff_cannot_check_in(self):
        with patch.object(
            frappe,
            "get_roles",
            return_value=["System Manager"]
        ):
            with self.assertRaises(frappe.ValidationError):
                check_in_with_qr("test_qr_token")

    def test_duplicate_qr_scan_is_rejected(self):
        valid_token = create_signed_qr_token()

        registration = frappe._dict({
            "name": "TEST-REG-001",
            "attendee": "TEST-ATTENDEE",
            "event": "TEST-EVENT",
            "ticket_type": "TEST-TICKET",
            "payment_status": "Paid",
            "registration_status": "Checked In",
            "checkin_time": "2026-11-24 10:00:00"
        })

        with patch.object(
            frappe,
            "get_roles",
            return_value=["Gate Staff"]
        ), patch.object(
            frappe.db,
            "get_value",
            side_effect=[
                "TEST-REG-001",
                frappe._dict(
                    attendee_name="Test Attendee",
                    attendee_email="test@example.com"
                )
            ]
        ), patch.object(
            frappe,
            "get_doc",
            return_value=registration
        ):
            result = check_in_with_qr(valid_token)

        self.assertFalse(result["success"])
        self.assertEqual(
            result["message"],
            "This attendee has already been checked in."
        )

    def test_confirmed_pending_payment_registration_can_check_in(self):
        valid_token = create_signed_qr_token()
        registration = frappe._dict({
            "name": "TEST-REG-PENDING-PAYMENT",
            "attendee": "TEST-ATTENDEE",
            "event": "TEST-EVENT",
            "ticket_type": "TEST-TICKET",
            "payment_status": "Pending",
            "registration_status": "Confirmed"
        })

        with patch.object(
            frappe,
            "get_roles",
            return_value=["Gate Staff"]
        ), patch.object(
            frappe.db,
            "get_value",
            side_effect=[
                registration.name,
                frappe._dict(
                    attendee_name="Test Attendee",
                    attendee_email="test@example.com"
                )
            ]
        ), patch.object(
            frappe,
            "get_doc",
            return_value=registration
        ), patch.object(
            frappe.db,
            "set_value"
        ):
            result = check_in_with_qr(valid_token)

        self.assertTrue(result["success"])
        self.assertEqual(result["payment_status"], "Pending")
        self.assertEqual(result["registration_status"], "Checked In")

    def test_my_registrations_only_returns_current_users_email(self):
        registration_rows = [
            frappe._dict(name="OWN-REGISTRATION", attendee_email="user@example.com"),
            frappe._dict(name="OTHER-REGISTRATION", attendee_email="other@example.com"),
        ]

        with patch.object(
            frappe,
            "session",
            frappe._dict(user="user@example.com"),
        ), patch.object(
            frappe.db,
            "get_value",
            return_value="user@example.com",
        ), patch.object(
            frappe,
            "get_all",
            side_effect=[
                [frappe._dict(name="OWN-ATTENDEE"), frappe._dict(name="OTHER-ATTENDEE")],
                [frappe._dict(name="OWN-REGISTRATION"), frappe._dict(name="OTHER-REGISTRATION")],
            ],
        ), patch(
            "event_management.event_management.doctype.event_registration.event_registration.add_attendee_details",
            return_value=registration_rows,
        ):
            result = get_my_registrations()

        self.assertEqual([row.name for row in result], ["OWN-REGISTRATION"])

    def test_attendee_session_only_returns_its_linked_registrations(self):
        attendee_name = "TEST-ATTENDEE-SESSION"
        access_token = create_attendee_access_token(attendee_name)
        attendee_records = [
            frappe._dict(name=attendee_name),
            frappe._dict(name="TEST-DUPLICATE-ATTENDEE"),
        ]
        registrations = [
            frappe._dict(name="TEST-ATTENDEE-REGISTRATION", attendee=attendee_name),
            frappe._dict(
                name="TEST-DUPLICATE-REGISTRATION",
                attendee="TEST-DUPLICATE-ATTENDEE",
            ),
        ]

        with patch.object(
            frappe.db,
            "exists",
            return_value=True,
        ), patch.object(
            frappe.db,
            "get_value",
            return_value="test@example.com",
        ), patch.object(
            frappe,
            "get_all",
            side_effect=[attendee_records, registrations],
        ) as get_all, patch(
            "event_management.event_management.doctype.event_attendee.api.add_attendee_details",
            side_effect=lambda rows: rows,
        ):
            result = get_attendee_registrations(attendee_name, access_token)

        self.assertTrue(verify_attendee_access_token(attendee_name, access_token))
        self.assertFalse(verify_attendee_access_token("OTHER-ATTENDEE", access_token))
        self.assertEqual(
            [row.name for row in result],
            [row.name for row in registrations],
        )
        self.assertEqual(
            get_all.call_args_list[1].kwargs["filters"],
            {"attendee": ["in", [attendee_name, "TEST-DUPLICATE-ATTENDEE"]]},
        )

    def test_existing_attendee_email_returns_already_registered_status(self):
        with patch.object(
            frappe,
            "get_all",
            return_value=[frappe._dict(name="EXISTING-ATTENDEE")],
        ), patch.object(
            frappe,
            "get_doc",
        ) as get_doc:
            result = register_attendee(
                "Attendee",
                "test@example.com",
                "123456789",
            )

        self.assertEqual(result, {"already_registered": True})
        get_doc.assert_not_called()

    def test_attendee_session_can_cancel_its_own_registration(self):
        attendee_name = "TEST-CANCEL-ATTENDEE"
        access_token = create_attendee_access_token(attendee_name)
        registration = frappe._dict(
            name="TEST-CANCEL-REGISTRATION",
            attendee=attendee_name,
            event="TEST-EVENT",
            registration_status="Confirmed",
        )
        event = frappe._dict(
            start_date="2027-01-01",
            start_time="10:00:00",
        )

        with patch.object(
            frappe,
            "session",
            frappe._dict(user="Guest"),
        ), patch.object(
            frappe,
            "get_doc",
            return_value=registration,
        ), patch.object(
            frappe.db,
            "get_value",
            return_value=event,
        ), patch.object(
            frappe.db,
            "set_value",
        ) as set_value:
            result = cancel_my_registration(
                registration.name,
                attendee=attendee_name,
                access_token=access_token,
            )

        self.assertTrue(result["success"])
        set_value.assert_called_once()

    def test_attendee_session_cannot_cancel_another_attendees_registration(self):
        attendee_name = "TEST-CANCEL-ATTENDEE"
        access_token = create_attendee_access_token(attendee_name)
        registration = frappe._dict(
            name="TEST-OTHER-REGISTRATION",
            attendee="OTHER-ATTENDEE",
            event="TEST-EVENT",
            registration_status="Confirmed",
        )

        with patch.object(
            frappe,
            "session",
            frappe._dict(user="Guest"),
        ), patch.object(
            frappe,
            "get_doc",
            return_value=registration,
        ), patch.object(
            frappe.db,
            "get_value",
            side_effect=["test@example.com", "other@example.com"],
        ):
            with self.assertRaises(frappe.ValidationError):
                cancel_my_registration(
                    registration.name,
                    attendee=attendee_name,
                    access_token=access_token,
                )

    def test_attendee_session_can_cancel_duplicate_email_registration(self):
        attendee_name = "TEST-CANONICAL-ATTENDEE"
        access_token = create_attendee_access_token(attendee_name)
        registration = frappe._dict(
            name="TEST-DUPLICATE-EMAIL-REGISTRATION",
            attendee="TEST-DUPLICATE-ATTENDEE",
            event="TEST-EVENT",
            registration_status="Confirmed",
        )
        event = frappe._dict(
            start_date="2027-01-01",
            start_time="10:00:00",
        )

        with patch.object(
            frappe,
            "session",
            frappe._dict(user="Guest"),
        ), patch.object(
            frappe,
            "get_doc",
            return_value=registration,
        ), patch.object(
            frappe.db,
            "get_value",
            side_effect=["test@example.com", "TEST@example.com", event],
        ), patch.object(
            frappe.db,
            "set_value",
        ) as set_value:
            result = cancel_my_registration(
                registration.name,
                attendee=attendee_name,
                access_token=access_token,
            )

        self.assertTrue(result["success"])
        set_value.assert_called_once()

    def test_ticket_token_can_cancel_its_own_registration(self):
        access_token = create_signed_qr_token()
        registration = frappe._dict(
            name="TEST-TICKET-CANCEL-REGISTRATION",
            attendee="TEST-TICKET-CANCEL-ATTENDEE",
            event="TEST-EVENT",
            qr_code_token=access_token,
            registration_status="Confirmed",
        )
        event = frappe._dict(
            start_date="2027-01-01",
            start_time="10:00:00",
        )

        with patch.object(
            frappe,
            "session",
            frappe._dict(user="Guest"),
        ), patch.object(
            frappe,
            "get_doc",
            return_value=registration,
        ), patch.object(
            frappe.db,
            "get_value",
            return_value=event,
        ), patch.object(
            frappe.db,
            "set_value",
        ) as set_value:
            result = cancel_my_registration(
                registration.name,
                access_token=access_token,
            )

        self.assertTrue(result["success"])
        set_value.assert_called_once()

    def test_invalid_qr_token_is_rejected(self):
        with patch.object(
            frappe,
            "get_roles",
            return_value=["Gate Staff"]
        ):
            with self.assertRaises(frappe.ValidationError):
                check_in_with_qr("invalid_qr_token")
