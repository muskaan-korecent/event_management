# Event Management Platform

An event booking application built using **Frappe Framework v16** and **Vue 3**.

Organizers can create events, manage ticket types and add-ons, and monitor registrations. Attendees can browse events, book tickets, view their registrations, and access QR tickets. Gate staff can verify tickets and check in attendees.

## Features

- Create and publish events.
- Manage different ticket types, prices, and ticket capacity.
- Add optional event add-ons with prices and stock limits.
- Register attendees and calculate the total registration amount.
- Generate a unique QR code for each registration.
- View, print, and download QR tickets.
- View and cancel eligible registrations.
- Check ticket capacity and add-on stock during registration.
- Provide an organizer dashboard with registration and revenue information.
- View check-in reports and export attendee details as CSV.
- Scan QR codes or search manually to check in attendees.
- Prevent duplicate check-ins.

## Frappe DocTypes

The backend is organized around the following DocTypes:

### 1. Managed Event

Stores the main event information.

- Event title and description
- Venue
- Start date and time
- End date and time
- Registration deadline
- Event status
- Organizer information

### 2. Event Ticket Type

Stores the different ticket options available for an event.

- Ticket name
- Linked event
- Ticket description
- Ticket price
- Ticket capacity

Organizers can create different ticket types for the same event.

### 3. Event Add-on

Stores optional products or services that attendees can select during registration.

- Add-on name
- Linked event
- Description
- Add-on price
- Available stock

### 4. Event Registration

Stores the attendee's booking information.

- Attendee details
- Linked event
- Selected ticket type
- Ticket price
- Add-on amount
- Total amount
- Payment status
- Registration status
- QR code token
- Check-in information

Each registration has its own QR code token, which is used for ticket verification and check-in.

### 5. Event Registration Add-on

A child table inside Event Registration.

It stores the add-ons selected by an attendee, including their details and amounts.

## Frontend Pages

The Vue frontend is served under `/event_management`.

### Attendee Pages

| Page | Route | Purpose |
|---|---|---|
| Register | `/event_management/register` | Enter attendee name, email, and phone number |
| Events | `/event_management/events` | Browse published events |
| Event Details | `/event_management/event/:name` | View event details, tickets, and add-ons |
| Book a Ticket | `/event_management/book-ticket/:name` | Select a ticket and add-ons and complete registration |
| My Registrations | `/event_management/my-registrations` | View registrations and manage eligible bookings |
| Ticket | `/event_management/ticket/:name` | View, print, or download the QR ticket |

### Organizer and Gate Staff Pages

| Page | Route | Purpose |
|---|---|---|
| Organizer Dashboard | `/event_management/dashboard` | View event totals, registrations, revenue, and monthly trends |
| Check-in Report | `/event_management/checkin-report` | View attendance information and export CSV reports |
| Gate Scanner | `/event_management/gate-scanner` | Scan QR tickets and check in attendees |

The organizer dashboard and check-in report require a Frappe login. Dashboard data is limited to events assigned to the logged-in organizer.

The gate scanner requires the **Gate Staff** role.

## Attendee Registration and Access

Attendees enter their name, email address, and phone number before booking an event.

The application saves an attendee profile, attendee ID, email address, and signed access token in the browser.

The **My Registrations** page uses the saved attendee ID and token to retrieve registrations. Attendees do not need a Frappe login for this flow.

The backend verifies the token and retrieves registrations linked to the attendee profile. The frontend also checks the email against the saved email address.

There is a separate access flow for users logged in to Frappe. In that case, registrations are retrieved by matching the logged-in account email with the attendee email.

## Booking and Check-in Flow

1. The organizer creates an event in Frappe Desk.
2. Ticket types and optional add-ons are configured for the event.
3. The attendee browses published events.
4. The attendee selects a ticket and any optional add-ons.
5. The system checks ticket capacity and add-on stock.
6. The registration is created and the total amount is calculated.
7. A unique QR code is generated for the registration.
8. The attendee can access their ticket from My Registrations.
9. Gate staff scan the QR code or search for the registration.
10. The system verifies the ticket and prevents duplicate check-ins.

Attendees can cancel eligible registrations before the event starts, provided they have not already checked in.

## Payment Status

The Event Registration DocType includes a payment status field to track payment information.

**Razorpay payment integration is not implemented yet.** Online payment processing and payment verification are still pending.

## Technology Stack

**Backend**
- Frappe Framework v16
- Python
- MariaDB

**Frontend**
- Vue 3
- TypeScript
- Vite
- Frappe UI

**Other**
- `html5-qrcode` for QR code scanning
- Git and GitHub

## Installation

A working Frappe Bench v16 environment is required.

From your bench directory, run:

```bash
bench get-app https://github.com/muskaan-korecent/event_management.git --branch version-16

bench --site your-site-name install-app event_management
```

Replace `your-site-name` with your actual Frappe site name.

## Run Locally

Install the frontend dependencies:

```bash
cd apps/event_management/frontend
npm install
```

Go back to your bench directory:

```bash
cd ../..
```

Start the development server:

```bash
bench start
```

The frontend is available under:

`/event_management`

To run the Vite development server separately:

```bash
cd apps/event_management/frontend
npm run dev
```

## Running Tests

From your bench directory, run:

```bash
bench --site your-site-name run-tests --app event_management
```

## License

MIT License. See [license.txt](license.txt).
