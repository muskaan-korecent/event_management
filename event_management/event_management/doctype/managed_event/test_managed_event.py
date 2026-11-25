# Copyright (c) 2026, Muskaan and Contributors
# See license.txt

import frappe
from unittest.mock import patch

from frappe.tests import IntegrationTestCase

from event_management.event_management.doctype.managed_event.managed_event import (
	get_public_event_booking_options,
)


# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]



class IntegrationTestManagedevent(IntegrationTestCase):
	"""
	Integration tests for Managedevent.
	Use this class for testing interactions between multiple components.
	"""

	def test_public_booking_options_calculate_ticket_availability(self):
		ticket = frappe._dict(
			name="TEST-TICKET",
			ticket_capacity=5,
		)

		with patch.object(
			frappe.db,
			"exists",
			return_value=True,
		), patch.object(
			frappe,
			"get_all",
			side_effect=[[ticket], []],
		), patch.object(
			frappe.db,
			"count",
			return_value=2,
		):
			options = get_public_event_booking_options("TEST-EVENT")

		self.assertEqual(options["tickets"][0].available_tickets, 3)
