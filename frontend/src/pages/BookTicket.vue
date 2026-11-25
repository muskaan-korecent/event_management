<script setup lang="ts">
import { computed, ref } from 'vue'
import { createResource } from 'frappe-ui'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const eventName = String(route.params.name)
const attendeeId = localStorage.getItem('event_attendee_id')
const selectedTicket = ref('')
const selectedAddons = ref<Record<string, number>>({})
const errorMessage = ref('')

interface Event {
  event_title: string
}

interface Ticket {
  name: string
  ticket_name: string
  ticket_price: number
  available_tickets: number
}

interface Addon {
  name: string
  addon_name: string
  addon_price: number
  available_stock: number
}

const event = createResource({
  url: 'event_management.event_management.doctype.managed_event.managed_event.get_published_event',
  params: { name: eventName },
  auto: true
})

const bookingOptions = createResource({
  url: 'event_management.event_management.doctype.managed_event.managed_event.get_public_event_booking_options',
  params: {
    name: eventName
  },
  auto: true
})

const eventData = computed(() => event.data as Event | null)
const ticketList = computed(() => (bookingOptions.data?.tickets || []) as Ticket[])
const addonList = computed(() => (bookingOptions.data?.addons || []) as Addon[])
const hasAvailableTicket = computed(() =>
  ticketList.value.some(ticket => ticket.available_tickets > 0)
)
const attendeeName = localStorage.getItem('event_attendee_name') || ''
const attendeeEmail = localStorage.getItem('event_attendee_email') || ''

const totalAmount = computed(() => {
  const ticket = ticketList.value.find(item => item.name === selectedTicket.value)
  const ticketPrice = Number(ticket?.ticket_price || 0)
  const addonTotal = addonList.value.reduce((total, addon) => {
    const quantity = Number(selectedAddons.value[addon.name] || 0)
    return total + quantity * Number(addon.addon_price || 0)
  }, 0)

  return ticketPrice + addonTotal
})

// Display-only helpers for the order summary
const selectedTicketData = computed(() =>
  ticketList.value.find(item => item.name === selectedTicket.value) || null
)

const selectedAddonLines = computed(() =>
  addonList.value
    .filter(addon => selectedAddons.value[addon.name])
    .map(addon => ({
      name: addon.name,
      label: addon.addon_name,
      quantity: Number(selectedAddons.value[addon.name] || 0),
      amount: Number(selectedAddons.value[addon.name] || 0) * Number(addon.addon_price || 0)
    }))
)

const registration = createResource({
  url: 'event_management.event_management.doctype.event_registration.api.register_for_event',

  onSuccess(result: { name: string; access_token: string }) {
    sessionStorage.setItem(`event_ticket_access_${result.name}`, result.access_token)
    router.push(`/ticket/${encodeURIComponent(result.name)}`)
  },

  onError(error: { messages?: string[] }) {
    errorMessage.value =
      error.messages?.join('\n') || 'Could not book this ticket. Please try again.'
  }
})

function toggleAddon(addonName: string, event: globalThis.Event) {
  const selected = (event.target as HTMLInputElement).checked

  if (selected) {
    selectedAddons.value[addonName] = 1
  } else {
    delete selectedAddons.value[addonName]
  }
}

function submitBooking() {
  errorMessage.value = ''

  if (!attendeeId) {
    router.push({
      path: '/register',
      query: { returnTo: route.fullPath }
    })
    return
  }

  if (!selectedTicket.value) {
    errorMessage.value = 'Please select a ticket type.'
    return
  }

  registration.submit({
    attendee: attendeeId,
    event: eventName,
    ticket_type: selectedTicket.value,
    addons: Object.entries(selectedAddons.value).map(([addon, quantity]) => ({
      addon,
      quantity
    }))
  })
}

function formatPrice(price: number) {
  return `₹${Number(price || 0).toFixed(2)}`
}
</script>

<template>
  <main class="page">

    <!-- Header -->
    <header class="hero">
      <div class="header-decoration"></div>

      <div class="hero-inner">
        <div class="topline">
          <div class="logo">
            <span class="logo-icon">✦</span>
            <span class="logo-text">EVENT MANAGEMENT</span>
          </div>

          <button
            class="btn-glass"
            @click="router.push(`/event/${encodeURIComponent(eventName)}`)"
          >
            ← &nbsp;Back to event
          </button>
        </div>

        <div class="hero-text">
          <span class="badge-gold">BOOKING</span>
          <h1>Book a Ticket</h1>
          <p>{{ eventData?.event_title || eventName }}</p>
        </div>
      </div>
    </header>

    <div class="container">

      <!-- Attendee -->
      <section class="card attendee-card">
        <div class="avatar">{{ (attendeeName || '?').charAt(0).toUpperCase() }}</div>
        <div class="attendee-info">
          <span class="label">BOOKING FOR</span>
          <strong>{{ attendeeName || 'Guest' }}</strong>
          <span v-if="attendeeEmail" class="attendee-email">{{ attendeeEmail }}</span>
        </div>
      </section>

      <!-- Tickets -->
      <section class="card section-pad">
        <div class="section-head">
          <span class="step">1</span>
          <div>
            <span class="label">STEP ONE</span>
            <h2>Choose a ticket</h2>
          </div>
        </div>

        <div v-if="bookingOptions.loading" class="state">
          <div class="spinner"></div>
          Loading tickets...
        </div>

        <p v-else-if="bookingOptions.error" role="alert" class="error-box">
          Could not load tickets. Please return to the event page and try again.
        </p>

        <p v-else-if="ticketList.length === 0" class="empty">
          No tickets are currently available.
        </p>

        <p v-else-if="!hasAvailableTicket" class="empty">
          All tickets for this event are sold out.
        </p>

        <div v-else class="option-list">
          <label
            v-for="ticket in ticketList"
            :key="ticket.name"
            class="option"
            :class="{
              selected: selectedTicket === ticket.name,
              disabled: ticket.available_tickets < 1
            }"
          >
            <span class="option-left">
              <input
                v-model="selectedTicket"
                type="radio"
                name="ticket-type"
                :value="ticket.name"
                :disabled="ticket.available_tickets < 1"
                class="native-input"
              />
              <span class="radio-dot"></span>
              <span>
                <strong class="option-title">{{ ticket.ticket_name }}</strong>
                <small
                  class="option-sub"
                  :class="ticket.available_tickets < 1 ? 'sold' : ''"
                >
                  {{ ticket.available_tickets < 1
                    ? 'Sold out'
                    : `${ticket.available_tickets} tickets available` }}
                </small>
              </span>
            </span>
            <strong class="option-price">{{ formatPrice(ticket.ticket_price) }}</strong>
          </label>
        </div>
      </section>

      <!-- Add-ons -->
      <section class="card section-pad">
        <div class="section-head">
          <span class="step gold">2</span>
          <div>
            <span class="label">STEP TWO · OPTIONAL</span>
            <h2>Add-ons</h2>
          </div>
        </div>

        <div v-if="bookingOptions.loading" class="state">
          <div class="spinner"></div>
          Loading add-ons...
        </div>

        <p v-else-if="bookingOptions.error" role="alert" class="error-box">
          Could not load add-ons. Please return to the event page and try again.
        </p>

        <p v-else-if="addonList.length === 0" class="empty">
          No add-ons are available for this event.
        </p>

        <div v-else class="option-list">
          <div
            v-for="addon in addonList"
            :key="addon.name"
            class="option addon"
            :class="{
              selected: Boolean(selectedAddons[addon.name]),
              disabled: addon.available_stock < 1
            }"
          >
            <label class="option-left">
              <input
                type="checkbox"
                :disabled="addon.available_stock < 1"
                :checked="Boolean(selectedAddons[addon.name])"
                class="native-input"
                @change="toggleAddon(addon.name, $event)"
              />
              <span class="check-box">✓</span>
              <span>
                <strong class="option-title">{{ addon.addon_name }}</strong>
                <small
                  class="option-sub"
                  :class="addon.available_stock < 1 ? 'sold' : ''"
                >
                  {{ addon.available_stock < 1
                    ? 'Out of stock'
                    : `${addon.available_stock} available` }}
                </small>
              </span>
            </label>

            <div class="addon-right">
              <strong class="option-price">{{ formatPrice(addon.addon_price) }}</strong>
              <input
                v-if="selectedAddons[addon.name]"
                v-model.number="selectedAddons[addon.name]"
                type="number"
                min="1"
                :max="addon.available_stock"
                aria-label="Add-on quantity"
                class="qty"
              />
            </div>
          </div>
        </div>
      </section>

      <!-- Summary -->
      <section class="summary">
        <div class="header-decoration"></div>

        <div class="summary-content">
          <span class="summary-label">ORDER SUMMARY</span>

          <div class="lines">
            <div class="line">
              <span>{{ selectedTicketData ? selectedTicketData.ticket_name : 'No ticket selected' }}</span>
              <span>{{ selectedTicketData ? formatPrice(selectedTicketData.ticket_price) : '—' }}</span>
            </div>

            <div v-for="line in selectedAddonLines" :key="line.name" class="line">
              <span>{{ line.label }} × {{ line.quantity }}</span>
              <span>{{ formatPrice(line.amount) }}</span>
            </div>
          </div>

          <div class="total-row">
            <span>Total</span>
            <strong>{{ formatPrice(totalAmount) }}</strong>
          </div>

          <p class="summary-note">
            Your ticket and QR code will be available immediately after booking.
          </p>

          <p v-if="errorMessage" role="alert" class="summary-error">
            {{ errorMessage }}
          </p>

          <button
            class="btn-gold"
            :disabled="registration.loading || bookingOptions.loading || !hasAvailableTicket"
            @click="submitBooking"
          >
            <span v-if="registration.loading" class="spinner-small"></span>
            <span v-if="registration.loading">Booking your ticket...</span>
            <span v-else>Book ticket &nbsp;→</span>
          </button>
        </div>
      </section>

    </div>
  </main>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: #f1f3f8;
  font-family: Arial, sans-serif;
  color: #202b43;
  padding-bottom: 50px;
}

/* Hero */
.hero {
  position: relative;
  overflow: hidden;
  background: linear-gradient(125deg, #182d58, #354e85);
  color: #ffffff;
  padding-bottom: 70px;
}

.hero-inner {
  position: relative;
  z-index: 2;
  max-width: 760px;
  margin: auto;
  padding: 22px 24px 0;
}

.header-decoration {
  position: absolute;
  width: 300px;
  height: 300px;
  right: -90px;
  top: -120px;
  border: 1px solid rgba(255, 255, 255, 0.17);
  border-radius: 50%;
  box-shadow: 0 0 0 34px rgba(255, 255, 255, 0.04),
              0 0 0 70px rgba(255, 255, 255, 0.035);
}

.topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  color: #f6d58c;
  font-size: 20px;
}

.logo-text {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 3px;
}

.btn-glass {
  padding: 10px 18px;
  border: 1px solid rgba(255, 255, 255, 0.35);
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-glass:hover {
  background: rgba(255, 255, 255, 0.2);
}

.hero-text {
  margin-top: 44px;
}

.badge-gold {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 30px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2px;
  color: #182d58;
  background: #f6d58c;
}

.hero-text h1 {
  margin: 16px 0 8px;
  font-size: 38px;
  font-weight: 750;
  color: #ffffff;
}

.hero-text p {
  margin: 0;
  font-size: 16px;
  color: #d7e0f5;
}

/* Layout */
.container {
  max-width: 760px;
  margin: -40px auto 0;
  padding: 0 24px;
  position: relative;
  z-index: 3;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card {
  background: #ffffff;
  border-radius: 18px;
  box-shadow: 0 12px 35px rgba(25, 40, 75, 0.1);
}

.section-pad {
  padding: 30px 32px;
}

.label {
  display: block;
  color: #8791a5;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1.5px;
}

/* Attendee */
.attendee-card {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 22px 28px;
}

.avatar {
  width: 52px;
  height: 52px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: linear-gradient(125deg, #182d58, #354e85);
  color: #f6d58c;
  font-size: 22px;
  font-weight: 700;
}

.attendee-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.attendee-info strong {
  font-size: 18px;
  color: #1c315d;
}

.attendee-email {
  font-size: 13px;
  color: #7b8495;
  overflow-wrap: anywhere;
}

/* Section head */
.section-head {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 22px;
}

.section-head h2 {
  margin: 4px 0 0;
  font-size: 23px;
  font-weight: 750;
  color: #1c315d;
}

.step {
  width: 38px;
  height: 38px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #354e85;
  color: #ffffff;
  font-weight: 700;
}

.step.gold {
  background: #f6d58c;
  color: #182d58;
}

/* Options */
.option-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  padding: 18px 20px;
  border: 1.5px solid #e3e7ef;
  border-radius: 14px;
  background: #fbfcfe;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s, transform 0.15s;
}

.option:hover:not(.disabled) {
  border-color: #b8c7ee;
  transform: translateY(-1px);
}

.option.selected {
  border-color: #354e85;
  background: #f3f6fd;
  box-shadow: 0 0 0 4px rgba(53, 78, 133, 0.1);
}

.option.disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.option-left {
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: inherit;
  min-width: 0;
}

.native-input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.radio-dot,
.check-box {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
  border: 2px solid #cbd2df;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.radio-dot {
  border-radius: 50%;
}

.check-box {
  border-radius: 6px;
  font-size: 13px;
  font-weight: 700;
  color: transparent;
}

.option.selected .radio-dot {
  border-color: #354e85;
  background: radial-gradient(circle, #354e85 45%, #ffffff 50%);
}

.option.selected .check-box {
  border-color: #354e85;
  background: #354e85;
  color: #ffffff;
}

.native-input:focus-visible ~ .radio-dot,
.native-input:focus-visible ~ .check-box {
  box-shadow: 0 0 0 4px rgba(53, 78, 133, 0.25);
}

.option-title {
  display: block;
  font-size: 16px;
  color: #26344f;
}

.option-sub {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #7b8495;
}

.option-sub.sold {
  color: #a33a2a;
  font-weight: 700;
}

.option-price {
  font-size: 18px;
  color: #1c315d;
}

.addon-right {
  display: flex;
  align-items: center;
  gap: 14px;
}

.qty {
  width: 70px;
  padding: 9px 10px;
  border: 1.5px solid #cbd2df;
  border-radius: 9px;
  background: #ffffff;
  font-size: 14px;
  font-weight: 600;
  color: #26344f;
  text-align: center;
  outline: none;
}

.qty:focus {
  border-color: #354e85;
  box-shadow: 0 0 0 4px rgba(53, 78, 133, 0.12);
}

.empty {
  margin: 0;
  color: #8993a6;
  font-size: 14px;
}

/* Summary */
.summary {
  position: relative;
  overflow: hidden;
  border-radius: 18px;
  padding: 32px 34px;
  background: linear-gradient(125deg, #182d58, #354e85);
  color: #ffffff;
  box-shadow: 0 15px 45px rgba(25, 40, 75, 0.2);
}

.summary-content {
  position: relative;
  z-index: 2;
}

.summary-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 3px;
  color: #c5d4f5;
}

.lines {
  margin-top: 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.line {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  font-size: 14px;
  color: #d7e0f5;
}

.total-row {
  margin-top: 20px;
  padding-top: 18px;
  border-top: 1px dashed rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.total-row span {
  font-size: 16px;
  color: #d7e0f5;
}

.total-row strong {
  font-size: 30px;
  color: #f6d58c;
}

.summary-note {
  margin: 14px 0 0;
  font-size: 13px;
  line-height: 1.5;
  color: #c5d4f5;
}

.summary-error {
  margin: 16px 0 0;
  padding: 12px 14px;
  white-space: pre-line;
  font-size: 13px;
  color: #ffd7d1;
  background: rgba(220, 70, 50, 0.25);
  border: 1px solid rgba(255, 180, 170, 0.4);
  border-radius: 10px;
}

.btn-gold {
  margin-top: 22px;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 17px;
  border: none;
  border-radius: 10px;
  background: #f6d58c;
  color: #182d58;
  font-size: 16px;
  font-weight: 750;
  cursor: pointer;
  box-shadow: 0 8px 22px rgba(0, 0, 0, 0.22);
  transition: transform 0.15s, box-shadow 0.15s, opacity 0.2s;
}

.btn-gold:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.3);
}

.btn-gold:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* States */
.state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 24px;
  color: #6b7589;
}

.error-box {
  margin: 0;
  padding: 14px 16px;
  font-size: 14px;
  color: #a33a2a;
  background: #fdecea;
  border: 1px solid #f6c9c3;
  border-radius: 12px;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #dfe5f2;
  border-top-color: #354e85;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(24, 45, 88, 0.3);
  border-top-color: #182d58;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 620px) {
  .hero-inner {
    padding: 18px 16px 0;
  }

  .logo-text {
    font-size: 11px;
    letter-spacing: 2px;
  }

  .hero-text {
    margin-top: 32px;
  }

  .hero-text h1 {
    font-size: 28px;
  }

  .container {
    padding: 0 12px;
  }

  .section-pad {
    padding: 24px 18px;
  }

  .summary {
    padding: 26px 22px;
  }

  .btn-glass {
    padding: 9px 12px;
    font-size: 13px;
  }
}
</style>