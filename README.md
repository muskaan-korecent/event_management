# Event Management Platform

A simple event booking app I built on **Frappe Framework v16** with a **Vue 3** frontend.

Organizers set up events, ticket types and add-ons, then keep an eye on registrations and revenue. Attendees browse events, book tickets and get a QR ticket. Gate staff scan those QR codes at the door to check people in.

## Screenshots

### Attendee side

**Register** – attendees start by entering their name, email and phone number.

 <img width="1550" height="930" alt="image" src="https://github.com/user-attachments/assets/058b75d9-e392-4d29-9a2f-ac133f6c8538" />


**Upcoming Events** – all published events in one place.

<img width="1400" height="840" alt="image" src="https://github.com/user-attachments/assets/71002512-51bc-4c54-952a-944581c77c98" />


**Event Details** – venue, dates, ticket types with live availability, and optional add-ons.

<img width="896" height="1359" alt="image" src="https://github.com/user-attachments/assets/95b3e9b3-adc8-424a-aceb-1bc345914331" />


**Book a Ticket** – pick a ticket, tick any add-ons, and see the order total update as you go.

<img width="1096" height="1092" alt="image" src="https://github.com/user-attachments/assets/2a9070bc-2674-4576-b7a5-1875af4c2494" />


**Event Pass** – the QR ticket, which can be printed or downloaded.

<img width="1065" height="1120" alt="image" src="https://github.com/user-attachments/assets/ab4a9b78-4852-4012-98cd-ab71488609d7" />


**My Registrations** – every booking in one list, with options to view the ticket or cancel.

<img width="1400" height="840" alt="image" src="https://github.com/user-attachments/assets/8e3f13cf-0696-4607-aa38-8c62fa8d75cb" />


### Organizer side

**Organizer Dashboard** – event totals, registrations, check-ins, revenue and monthly trends, plus the latest registrations.

<img width="1204" height="1006" alt="image" src="https://github.com/user-attachments/assets/3c30d00d-ebdb-46e3-b08f-60c90b4efdb3" />


**Check-in Report** – attendance numbers, a per-event filter, attendee details and CSV export.

<img width="1288" height="938" alt="image" src="https://github.com/user-attachments/assets/7ffc02bf-0727-4472-9317-4f5532631883" />


### Gate staff side

**Gate Scanner** – staff scan a ticket's QR code or check someone in manually.

<!-- add Gate Scanner screenshot here -->


## What it does

- Create and publish events
- Set up multiple ticket types with their own prices and capacity
- Offer optional add-ons (lunch, t-shirts, etc.) with prices and stock limits
- Save attendee details (name, email, phone) when someone registers
- Register attendees and work out the total automatically
- Generate a unique QR code for every registration
- View, print and download tickets
- Let attendees view and cancel eligible bookings
- Check ticket capacity and add-on stock at booking time
- Show organizers a dashboard with registration and revenue numbers
- Show check-in reports and export attendee details as CSV
- Check people in by scanning a QR code or manually
- Block duplicate check-ins

## DocTypes

The backend is built around six DocTypes.

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

### 4. Event Attendee

The attendee profile created when someone registers on the Register page.

- Name
- Email
- Phone number

This profile is what the browser's attendee ID and access token refer to when attendees view their registrations.

### 5. Event Registration

One record per booking.

- Attendee details
- Linked event and selected ticket type
- Ticket price, add-on amount and total amount
- Payment status and registration status
- QR code token
- Check-in information

Each registration gets its own QR token, which is what gets verified at the gate.

### 6. Event Registration Add-on

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
| Gate Scanner | `/event_management/gate-scanner` | Scan QR tickets or check people in manually |

The dashboard and check-in report need a Frappe login, and the dashboard only shows events assigned to the logged-in organizer.

## Gate Scanner

The gate scanner is for staff at the entrance, and it needs the **Gate Staff** role. There are two ways to check someone in:

- **QR scan:** scan the QR code on the attendee's ticket (powered by `html5-qrcode`).
- **Manual check-in:** if a QR code won't scan, or the attendee can't show their ticket, search for their registration and check them in by hand.

Either way, the system verifies the registration and records the check-in. If the ticket has already been used, the second check-in is blocked. Checked-in attendees then show up in the organizer's Check-in Report.

## How attendee access works

Attendees give their name, email and phone number before booking. The app then stores an attendee profile, attendee ID, email and a signed access token in the browser.

My Registrations uses that saved ID and token to fetch bookings, so attendees don't need a Frappe account. The backend verifies the token and returns the registrations linked to that attendee profile, and the frontend also checks the email against the one saved in the browser.

If someone is logged in to Frappe, there's a separate path: their registrations are found by matching their account email to the attendee email.

## Booking and check-in flow

1. The organizer creates an event in Frappe Desk.
2. Ticket types and optional add-ons are set up for it.
3. An attendee browses the published events.
4. They pick a ticket and any add-ons.
5. The system checks ticket capacity and add-on stock.
6. The registration is created and the total is calculated.
7. A unique QR code is generated.
8. The attendee opens their ticket from My Registrations.
9. At the event, gate staff scan the QR code or check the attendee in manually.
10. The system verifies the ticket and stops duplicate check-ins.

Attendees can cancel an eligible registration any time before the event starts, as long as they haven't already checked in.

## Payments

Registrations have a payment status field, but **Razorpay is not integrated yet**. Online payments and payment verification are still on the to-do list, which is why every booking currently shows "Pending".




