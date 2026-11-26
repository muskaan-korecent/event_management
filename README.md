# Event Management Platform

A simple event booking app I built on **Frappe Framework v16** with a **Vue 3** frontend.

Organizers set up events, ticket types and add-ons, then keep an eye on registrations and revenue. Attendees browse events, book tickets and get a QR ticket. Gate staff scan those QR codes at the door to check people in.

## Screenshots

### Attendee side

**Register** – attendees start by entering their name, email and phone number.

 <img width="1550" height="930" alt="image" src="https://github.com/user-attachments/assets/058b75d9-e392-4d29-9a2f-ac133f6c8538" />


**Upcoming Events** – all published events in one place.

![Events list](screenshots/02-events.png)

**Event Details** – venue, dates, ticket types with live availability, and optional add-ons.

![Event details](screenshots/03-event-details.png)

**Book a Ticket** – pick a ticket, tick any add-ons, and see the order total update as you go.

![Book a ticket](screenshots/04-book-ticket.png)

**Event Pass** – the QR ticket, which can be printed or downloaded.

![QR ticket](screenshots/05-ticket.png)

**My Registrations** – every booking in one list, with options to view the ticket or cancel.

![My registrations](screenshots/06-my-registrations.png)

### Organizer side

**Organizer Dashboard** – event totals, registrations, check-ins, revenue and monthly trends, plus the latest registrations.

![Organizer dashboard](screenshots/07-dashboard.png)

**Check-in Report** – attendance numbers, a per-event filter, attendee details and CSV export.

![Check-in report](screenshots/08-checkin-report.png)

## What it does

- Create and publish events
- Set up multiple ticket types with their own prices and capacity
- Offer optional add-ons (lunch, t-shirts, etc.) with prices and stock limits
- Register attendees and work out the total automatically
- Generate a unique QR code for every registration
- View, print and download tickets
- Let attendees view and cancel eligible bookings
- Check ticket capacity and add-on stock at booking time
- Show organizers a dashboard with registration and revenue numbers
- Show check-in reports and export attendee details as CSV
- Check people in by scanning a QR code or searching manually
- Block duplicate check-ins

## DocTypes

The backend is built around five DocTypes.

### 1. Managed Event

The main event record.

- Title and description
- Venue
- Start and end date/time
- Registration deadline
- Event status
- Organizer

### 2. Event Ticket Type

The ticket options for an event. An event can have as many ticket types as you like.

- Ticket name and description
- Linked event
- Price
- Capacity

### 3. Event Add-on

Optional extras attendees can pick while booking.

- Add-on name and description
- Linked event
- Price
- Available stock

### 4. Event Registration

One record per booking.

- Attendee details
- Linked event and selected ticket type
- Ticket price, add-on amount and total amount
- Payment status and registration status
- QR code token
- Check-in information

Each registration gets its own QR token, which is what gets verified at the gate.

### 5. Event Registration Add-on

A child table inside Event Registration. It holds the add-ons the attendee picked, along with their details and amounts.

## Frontend Pages

The Vue app is served under `/event_management`.

### Attendee pages

| Page | Route | What it's for |
|---|---|---|
| Register | `/event_management/register` | Enter name, email and phone number |
| Events | `/event_management/events` | Browse published events |
| Event Details | `/event_management/event/:name` | See event info, tickets and add-ons |
| Book a Ticket | `/event_management/book-ticket/:name` | Choose a ticket and add-ons, then register |
| My Registrations | `/event_management/my-registrations` | View and manage your bookings |
| Ticket | `/event_management/ticket/:name` | View, print or download the QR ticket |

### Organizer and gate staff pages

| Page | Route | What it's for |
|---|---|---|
| Organizer Dashboard | `/event_management/dashboard` | Totals, registrations, revenue and monthly trends |
| Check-in Report | `/event_management/checkin-report` | Attendance details and CSV export |
| Gate Scanner | `/event_management/gate-scanner` | Scan QR tickets and check people in |

The dashboard and check-in report need a Frappe login, and the dashboard only shows events assigned to the logged-in organizer. The gate scanner needs the **Gate Staff** role.

## How attendee access works

Attendees give their name, email and phone number before booking. The app then stores an attendee profile, attendee ID, email and a signed access token in the browser.

My Registrations uses that saved ID and token to fetch bookings, so attendees don't need a Frappe account. The backend verifies the token and returns the registrations linked to that attendee profile, and
