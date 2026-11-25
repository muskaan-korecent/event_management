<script setup lang="ts">
import { computed } from 'vue'
import { createResource } from 'frappe-ui'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const eventName = String(route.params.name)

interface Event {
  name: string
  event_title: string
  description?: string
  venue?: string
  venue_address?: string
  start_date?: string
  start_time?: string
  end_date?: string
  end_time?: string
  cover_image?: string
  event_category?: string
  organizer?: string
  registration_deadline?: string
  max_attendees?: number
}

interface Ticket {
  name: string
  ticket_name: string
  ticket_price: number
  ticket_capacity: number
  available_tickets: number
  ticket_description?: string
}

interface Addon {
  name: string
  addon_name: string
  addon_price: number
  available_stock: number
  addon_description?: string
}

const event = createResource({
  url: 'event_management.event_management.doctype.managed_event.managed_event.get_published_event',
  params: { name: eventName },
  auto: true
})

const bookingOptions = createResource({
  url: 'event_management.event_management.doctype.managed_event.managed_event.get_public_event_booking_options',
  params: { name: eventName },
  auto: true
})

const eventData = computed(() => event.data as Event | null)
const ticketList = computed(() => (bookingOptions.data?.tickets || []) as Ticket[])
const addonList = computed(() => (bookingOptions.data?.addons || []) as Addon[])

function formatDate(date?: string) {
  if (!date) return 'Not announced'

  const isoDate = /^\d{2}-\d{2}-\d{4}$/.test(date)
    ? date.split('-').reverse().join('-')
    : date

  const parsedDate = new Date(`${isoDate}T00:00:00`)

  if (Number.isNaN(parsedDate.getTime())) return date

  return parsedDate.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

function formatPrice(price?: number) {
  return `₹${Number(price || 0).toFixed(2)}`
}
</script>

<template>
  <div class="page">

    <!-- Header -->
    <header class="topbar">
      <div class="topbar-inner">
        <div class="logo">
          <span class="logo-icon">✦</span>
          <span class="logo-text">EVENT MANAGEMENT</span>
        </div>

        <button class="btn-outline" @click="router.push('/events')">
          ← &nbsp;Back to Events
        </button>
      </div>
    </header>

    <main class="container">

      <!-- Loading -->
      <div v-if="event.loading" class="message">
        <div class="spinner"></div>
        Loading event details...
      </div>

      <!-- Error -->
      <div v-else-if="event.error" class="message">
        <p>Unable to load event details.</p>
        <button class="btn-outline" @click="event.reload()">Try Again</button>
      </div>

      <template v-else-if="eventData">

        <!-- Hero / event info -->
        <section class="card">

          <div v-if="eventData.cover_image" class="cover">
            <img :src="eventData.cover_image" :alt="eventData.event_title" />
            <div class="cover-overlay"></div>
          </div>

          <div v-else class="cover-fallback">
            <div class="header-decoration"></div>
            <span class="fallback-icon">✦</span>
          </div>

          <div class="card-body">
            <div class="tags">
              <span class="badge-live">● Published</span>
              <span v-if="eventData.event_category" class="badge-category">
                {{ eventData.event_category }}
              </span>
            </div>

            <h2 class="event-title">{{ eventData.event_title }}</h2>

            <div
              v-if="eventData.description"
              class="description"
              v-html="eventData.description"
            />
            <p v-else class="description">
              More information about this event will be available soon.
            </p>

            <div class="divider"></div>

            <div class="details-grid">
              <div class="detail">
                <span class="label">VENUE</span>
                <strong>{{ eventData.venue || 'Not announced' }}</strong>
              </div>

              <div class="detail">
                <span class="label">ADDRESS</span>
                <strong>{{ eventData.venue_address || 'Not announced' }}</strong>
              </div>

              <div class="detail">
                <span class="label">START DATE</span>
                <strong>{{ formatDate(eventData.start_date) }}</strong>
              </div>

              <div class="detail">
                <span class="label">START TIME</span>
                <strong>{{ eventData.start_time || 'Not announced' }}</strong>
              </div>

              <div class="detail">
                <span class="label">END DATE</span>
                <strong>{{ formatDate(eventData.end_date) }}</strong>
              </div>

              <div class="detail">
                <span class="label">END TIME</span>
                <strong>{{ eventData.end_time || 'Not announced' }}</strong>
              </div>

              <div class="detail">
                <span class="label">CATEGORY</span>
                <strong>{{ eventData.event_category || 'Not specified' }}</strong>
              </div>

              <div class="detail">
                <span class="label">ORGANIZER</span>
                <strong>{{ eventData.organizer || 'Not specified' }}</strong>
              </div>
            </div>
          </div>
        </section>

        <!-- Tickets -->
        <section class="card section-pad">
          <div class="section-head">
            <span class="label">ADMISSION</span>
            <h2>Available Tickets</h2>
          </div>

          <div v-if="bookingOptions.loading" class="message small">
            <div class="spinner"></div>
            Loading tickets...
          </div>

          <div v-else-if="bookingOptions.error" class="error-box">
            Unable to load ticket information.
            <button class="btn-outline" @click="bookingOptions.reload()">Try Again</button>
          </div>

          <p v-else-if="ticketList.length === 0" class="empty">
            No tickets are available for this event yet.
          </p>

          <div v-else class="item-list">
            <div v-for="ticket in ticketList" :key="ticket.name" class="item ticket-item">
              <div class="item-top">
                <div>
                  <h3>{{ ticket.ticket_name }}</h3>
                  <p class="item-desc">{{ ticket.ticket_description }}</p>
                </div>
                <div class="price">{{ formatPrice(ticket.ticket_price) }}</div>
              </div>

              <div class="item-meta">
                <span class="chip">Capacity: {{ ticket.ticket_capacity }}</span>
                <span
                  class="chip"
                  :class="ticket.available_tickets > 0 ? 'chip-green' : 'chip-red'"
                >
                  {{ ticket.available_tickets > 0
                    ? `${ticket.available_tickets} available`
                    : 'Sold out' }}
                </span>
              </div>
            </div>
          </div>
        </section>

        <!-- Add-ons -->
        <section class="card section-pad">
          <div class="section-head">
            <span class="label">EXTRAS</span>
            <h2>Optional Add-ons</h2>
          </div>

          <div v-if="bookingOptions.loading" class="message small">
            <div class="spinner"></div>
            Loading add-ons...
          </div>

          <div v-else-if="bookingOptions.error" class="error-box">
            Unable to load add-on information.
            <button class="btn-outline" @click="bookingOptions.reload()">Try Again</button>
          </div>

          <p v-else-if="addonList.length === 0" class="empty">
            No optional add-ons available.
          </p>

          <div v-else class="item-list">
            <div v-for="addon in addonList" :key="addon.name" class="item addon-item">
              <div class="item-top">
                <div>
                  <h3>{{ addon.addon_name }}</h3>
                  <p class="item-desc">{{ addon.addon_description }}</p>
                </div>
                <div class="price">{{ formatPrice(addon.addon_price) }}</div>
              </div>

              <div class="item-meta">
                <span class="chip">Stock: {{ addon.available_stock }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Call to action -->
        <section class="cta">
          <div class="header-decoration"></div>
          <div class="cta-content">
            <div class="cta-icon">✦</div>
            <h2>Interested in Attending?</h2>
            <p>Complete your registration to reserve your place at this event.</p>
            <button
              class="btn-gold"
              @click="router.push(`/book-ticket/${encodeURIComponent(eventName)}`)"
            >
              Book a Ticket &nbsp;→
            </button>
          </div>
        </section>

      </template>
    </main>

    
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: #f1f3f8;
  font-family: Arial, sans-serif;
  color: #202b43;
}

/* Top bar */
.topbar {
  background: linear-gradient(125deg, #182d58, #354e85);
  box-shadow: 0 4px 18px rgba(24, 45, 88, 0.18);
}

.topbar-inner {
  max-width: 980px;
  margin: auto;
  padding: 18px 24px;
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
  color: #ffffff;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 3px;
}

.topbar .btn-outline {
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.35);
  background: rgba(255, 255, 255, 0.08);
}

.topbar .btn-outline:hover {
  background: rgba(255, 255, 255, 0.18);
}

/* Layout */
.container {
  max-width: 980px;
  margin: auto;
  padding: 36px 24px 50px;
  display: flex;
  flex-direction: column;
  gap: 26px;
}

.card {
  background: #ffffff;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 15px 45px rgba(25, 40, 75, 0.1);
}

.section-pad {
  padding: 32px 36px;
}

/* Cover */
.cover {
  position: relative;
  height: 300px;
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.cover-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 50%, rgba(24, 45, 88, 0.45));
}

.cover-fallback {
  position: relative;
  height: 150px;
  overflow: hidden;
  background: linear-gradient(125deg, #182d58, #354e85);
  display: flex;
  align-items: center;
  justify-content: center;
}

.fallback-icon {
  font-size: 44px;
  color: #f6d58c;
  position: relative;
  z-index: 2;
}

.header-decoration {
  position: absolute;
  width: 240px;
  height: 240px;
  right: -75px;
  top: -95px;
  border: 1px solid rgba(255, 255, 255, 0.17);
  border-radius: 50%;
  box-shadow: 0 0 0 28px rgba(255, 255, 255, 0.04),
              0 0 0 58px rgba(255, 255, 255, 0.035);
}

/* Event info */
.card-body {
  padding: 34px 38px 38px;
}

.tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.badge-live {
  padding: 7px 13px;
  border-radius: 30px;
  font-size: 12px;
  font-weight: 700;
  color: #18764a;
  background: #e4f6eb;
}

.badge-category {
  padding: 7px 13px;
  border-radius: 30px;
  font-size: 12px;
  font-weight: 700;
  color: #354e85;
  background: #e8edf9;
}

.event-title {
  margin: 18px 0 14px;
  font-size: 34px;
  font-weight: 750;
  color: #1c315d;
  line-height: 1.2;
}

.description {
  color: #6b7589;
  font-size: 15px;
  line-height: 1.7;
}

.description :deep(p) {
  margin: 0 0 10px;
}

.divider {
  border-top: 1px dashed #cbd2df;
  margin: 28px 0;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 26px 24px;
}

.detail {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.detail strong {
  color: #26344f;
  font-size: 15px;
  overflow-wrap: anywhere;
}

.label {
  color: #8791a5;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1.5px;
}

/* Section heads */
.section-head {
  margin-bottom: 22px;
}

.section-head h2 {
  margin: 6px 0 0;
  font-size: 25px;
  font-weight: 750;
  color: #1c315d;
}

/* Items */
.item-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.item {
  position: relative;
  padding: 20px 22px 20px 26px;
  border: 1px solid #e3e7ef;
  border-radius: 14px;
  background: #fbfcfe;
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
}

.item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 14px;
  bottom: 14px;
  width: 4px;
  border-radius: 4px;
  background: #354e85;
}

.addon-item::before {
  background: #f6d58c;
}

.item:hover {
  transform: translateY(-2px);
  border-color: #cbd2df;
  box-shadow: 0 10px 26px rgba(25, 40, 75, 0.09);
}

.item-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  flex-wrap: wrap;
}

.item h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #26344f;
}

.item-desc {
  margin: 6px 0 0;
  font-size: 14px;
  color: #7b8495;
  line-height: 1.5;
}

.price {
  font-size: 21px;
  font-weight: 750;
  color: #1c315d;
}

.item-meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 16px;
}

.chip {
  padding: 6px 12px;
  border-radius: 30px;
  font-size: 12px;
  font-weight: 600;
  color: #5c667b;
  background: #eef1f7;
}

.chip-green {
  color: #18764a;
  background: #e4f6eb;
}

.chip-red {
  color: #a33a2a;
  background: #fdecea;
}

.empty {
  margin: 0;
  color: #8993a6;
  font-size: 14px;
}

/* CTA */
.cta {
  position: relative;
  overflow: hidden;
  border-radius: 18px;
  padding: 46px 30px;
  text-align: center;
  color: #ffffff;
  background: linear-gradient(125deg, #182d58, #354e85);
  box-shadow: 0 15px 45px rgba(25, 40, 75, 0.18);
}

.cta-content {
  position: relative;
  z-index: 2;
}

.cta-icon {
  font-size: 30px;
  color: #f6d58c;
}

.cta h2 {
  margin: 12px 0 8px;
  font-size: 28px;
  font-weight: 750;
}

.cta p {
  margin: 0 auto;
  max-width: 420px;
  color: #d7e0f5;
  font-size: 15px;
  line-height: 1.6;
}

/* Buttons */
.btn-outline {
  padding: 10px 18px;
  border: 1px solid #354e85;
  border-radius: 9px;
  background: #ffffff;
  color: #354e85;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-outline:hover {
  background: #f0f3fb;
}

.btn-gold {
  margin-top: 26px;
  padding: 16px 34px;
  border: none;
  border-radius: 10px;
  background: #f6d58c;
  color: #182d58;
  font-size: 15px;
  font-weight: 750;
  cursor: pointer;
  box-shadow: 0 8px 22px rgba(0, 0, 0, 0.2);
  transition: transform 0.15s, box-shadow 0.15s;
}

.btn-gold:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.28);
}

/* States */
.message {
  background: #ffffff;
  padding: 50px 30px;
  border-radius: 16px;
  text-align: center;
  color: #6b7589;
  box-shadow: 0 10px 30px rgba(25, 40, 75, 0.08);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}

.message.small {
  box-shadow: none;
  padding: 24px;
}

.error-box {
  padding: 16px 18px;
  color: #a33a2a;
  background: #fdecea;
  border: 1px solid #f6c9c3;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.spinner {
  width: 26px;
  height: 26px;
  border: 3px solid #dfe5f2;
  border-top-color: #354e85;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.footer {
  padding: 22px;
  text-align: center;
  font-size: 12px;
  color: #8b94a5;
}

@media (max-width: 640px) {
  .topbar-inner {
    padding: 14px 16px;
  }

  .logo-text {
    font-size: 11px;
    letter-spacing: 2px;
  }

  .container {
    padding: 22px 12px 40px;
  }

  .cover {
    height: 210px;
  }

  .card-body,
  .section-pad {
    padding: 24px 20px;
  }

  .event-title {
    font-size: 26px;
  }

  .details-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}
</style>