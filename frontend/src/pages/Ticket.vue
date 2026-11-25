
<script setup lang="ts">
import { computed } from 'vue'
import { createResource } from 'frappe-ui'
import { useRoute } from 'vue-router'

const route = useRoute()
const registrationName = String(route.params.name)
const accessToken = sessionStorage.getItem(
  `event_ticket_access_${registrationName}`
) || ''

const registration = createResource({
  url: 'event_management.event_management.doctype.event_registration.api.get_ticket_details',
  params: {
    registration_name: registrationName,
    access_token: accessToken
  },
  auto: true
})

interface TicketDetails {
  name: string
  event: string
  attendee_name: string
  attendee_email: string
  attendee_phone: string
  ticket_type: string
  ticket_price: number
  total_amount: number
  payment_status: string
  registration_status: string
  qr_code_data: string
}

const data = computed(() => registration.data as TicketDetails | null)

const isReady = computed(() => {
  return Boolean(
    data.value
      && ['Confirmed', 'Checked In'].includes(data.value.registration_status)
      && data.value.qr_code_data
  )
})

const qrImage = computed(() => data.value?.qr_code_data || '')

function downloadTicket() {
  window.print()
}
</script>

<template>
  <main class="ticket-page">
    <div class="ticket-wrapper">

      <div v-if="registration.loading" class="message">
        Loading your ticket...
      </div>

      <div v-else-if="registration.error" class="message">
        Unable to load your ticket. Please try again.
      </div>

      <div v-else-if="data" class="ticket">

        <header class="ticket-header">
          <div class="header-content">
            <div class="brand">EVENT MANAGEMENT</div>
            <div class="header-icon">✦</div>
            <h1>Your Event Pass</h1>
            <p>Your experience starts here.</p>
          </div>
          <div class="header-decoration"></div>
        </header>

        <section class="ticket-body">

          <div class="status-row">
            <span class="section-label">ADMISSION TICKET</span>

            <span v-if="isReady" class="status confirmed">
              ● Confirmed
            </span>

            <span v-else class="status pending">
              ● Pending
            </span>
          </div>

          <div class="event-name">
            <span class="muted-label">EVENT</span>
            <h2>{{ data.event }}</h2>
          </div>

          <div class="details-grid">

            <div class="detail">
              <span class="muted-label">ATTENDEE NAME</span>
              <strong>{{ data.attendee_name }}</strong>
            </div>

            <div class="detail">
              <span class="muted-label">EMAIL ADDRESS</span>
              <strong>{{ data.attendee_email }}</strong>
            </div>

            <div class="detail">
              <span class="muted-label">PHONE NUMBER</span>
              <strong>{{ data.attendee_phone }}</strong>
            </div>

            <div class="detail">
              <span class="muted-label">TICKET TYPE</span>
              <strong>{{ data.ticket_type }}</strong>
            </div>

            <div class="detail">
              <span class="muted-label">TICKET PRICE</span>
              <strong>₹{{ data.ticket_price }}</strong>
            </div>

            <div class="detail">
              <span class="muted-label">REGISTRATION ID</span>
              <strong>{{ data.name }}</strong>
            </div>

            <div class="detail">
              <span class="muted-label">TOTAL AMOUNT</span>
              <strong>₹{{ data.total_amount }}</strong>
            </div>

            <div class="detail">
              <span class="muted-label">PAYMENT STATUS</span>
              <strong>{{ data.payment_status }}</strong>
            </div>

          </div>

          <div class="divider"></div>

          <section class="qr-section">
            <template v-if="isReady">
              <h3>Your Entry QR Code</h3>
              <p>Present this QR code at the event entrance.</p>

              <div v-if="qrImage" class="qr-frame">
                <img :src="qrImage" alt="Event entry QR code" />
              </div>

              <p v-else class="warning">
                Your QR code is not available. Please contact the organizer.
              </p>

              <span class="qr-caption">
                KEEP THIS TICKET SAFE
              </span>
            </template>

            <template v-else>
              <div class="pending-icon">◷</div>
              <h3>Ticket Awaiting Approval</h3>
              <p>
                Your registration has been received. If your QR code is not
                available yet, refresh this page or contact the event organizer.
              </p>

              <button
                class="refresh-button"
                @click="registration.reload()"
              >
                Refresh Ticket Status
              </button>
            </template>
          </section>

          <div class="ticket-footer">
            <span>REGISTRATION ID</span>
            <strong>{{ data.name }}</strong>
            <p>Thank you for registering. We look forward to seeing you!</p>
          </div>

          <button
            v-if="isReady && qrImage"
            class="download-button"
            @click="downloadTicket"
          >
            ↓ &nbsp; Download / Print Ticket
          </button>

        </section>
      </div>

      <p class="page-note">
        Please keep your ticket ready when arriving at the event.
      </p>

    </div>
  </main>
</template>

<style scoped>
.ticket-page {
  min-height: 100vh;
  background: #f1f3f8;
  padding: 55px 18px;
  font-family: Arial, sans-serif;
  color: #202b43;
}

.ticket-wrapper {
  max-width: 680px;
  margin: auto;
}

.ticket {
  background: #ffffff;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 15px 45px rgba(25, 40, 75, 0.12);
}

.ticket-header {
  position: relative;
  overflow: hidden;
  background: linear-gradient(125deg, #182d58, #354e85);
  color: white;
  padding: 38px 42px 45px;
}

.header-content {
  position: relative;
  z-index: 2;
}

.brand {
  font-size: 11px;
  letter-spacing: 3px;
  font-weight: 700;
  color: #c5d4f5;
}

.header-icon {
  margin-top: 27px;
  font-size: 30px;
  color: #f6d58c;
}

.ticket-header h1 {
  margin: 12px 0 7px;
  font-size: 34px;
  font-weight: 750;
  color: white;
}

.ticket-header p {
  margin: 0;
  color: #d7e0f5;
  font-size: 14px;
}

.header-decoration {
  position: absolute;
  width: 240px;
  height: 240px;
  right: -75px;
  top: -95px;
  border: 1px solid rgba(255,255,255,0.17);
  border-radius: 50%;
  box-shadow: 0 0 0 28px rgba(255,255,255,0.04),
              0 0 0 58px rgba(255,255,255,0.035);
}

.ticket-body {
  padding: 35px 42px;
}

.status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.section-label,
.muted-label {
  color: #8791a5;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1.5px;
}

.status {
  padding: 8px 13px;
  border-radius: 30px;
  font-size: 12px;
  font-weight: 700;
}

.confirmed {
  color: #18764a;
  background: #e4f6eb;
}

.pending {
  color: #986817;
  background: #fff2d8;
}

.event-name {
  margin: 30px 0;
}

.event-name h2 {
  font-size: 27px;
  color: #1c315d;
  margin: 8px 0 0;
  font-weight: 750;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 26px 20px;
}

.detail {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.detail strong {
  color: #26344f;
  font-size: 14px;
  overflow-wrap: anywhere;
}

.divider {
  border-top: 1px dashed #cbd2df;
  margin: 34px 0;
}

.qr-section {
  text-align: center;
  padding: 5px 0 15px;
}

.qr-section h3 {
  color: #1c315d;
  font-size: 21px;
  font-weight: 750;
  margin: 0 0 9px;
}

.qr-section > p {
  color: #7b8495;
  font-size: 13px;
  line-height: 1.6;
}

.qr-frame {
  display: inline-flex;
  padding: 15px;
  border: 1px solid #e3e7ef;
  border-radius: 15px;
  margin: 20px 0 10px;
  background: white;
}

.qr-frame img {
  width: 205px;
  height: 205px;
  object-fit: contain;
}

.qr-caption {
  display: block;
  color: #8993a6;
  font-size: 10px;
  letter-spacing: 2px;
  font-weight: 700;
  margin-top: 12px;
}

.pending-icon {
  font-size: 43px;
  color: #c28b36;
  margin-bottom: 15px;
}

.warning {
  color: #a35b27 !important;
}

.refresh-button {
  margin-top: 14px;
  border: 1px solid #354e85;
  color: #354e85;
  background: white;
  padding: 11px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.ticket-footer {
  border-top: 1px dashed #cbd2df;
  margin-top: 25px;
  padding-top: 23px;
  text-align: center;
}

.ticket-footer span {
  display: block;
  color: #8993a6;
  font-size: 10px;
  letter-spacing: 1.5px;
}

.ticket-footer strong {
  display: block;
  margin-top: 7px;
  color: #26344f;
  font-size: 13px;
}

.ticket-footer p {
  color: #8993a6;
  font-size: 12px;
  margin-top: 17px;
}

.download-button {
  display: block;
  width: 100%;
  margin-top: 25px;
  padding: 15px;
  border: none;
  border-radius: 9px;
  color: white;
  background: #263f70;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.download-button:hover {
  background: #182d58;
}

.page-note {
  text-align: center;
  color: #8b94a5;
  font-size: 12px;
  margin-top: 20px;
}

.message {
  background: white;
  padding: 40px;
  border-radius: 15px;
  text-align: center;
}

@media (max-width: 550px) {
  .ticket-page {
    padding: 20px 10px;
  }

  .ticket-header {
    padding: 30px 24px;
  }

  .ticket-header h1 {
    font-size: 27px;
  }

  .ticket-body {
    padding: 25px 22px;
  }

  .details-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}

@media print {
  .ticket-page {
    background: white;
    padding: 0;
  }

  .ticket {
    box-shadow: none;
    border: 1px solid #ddd;
  }

  .download-button,
  .page-note {
    display: none !important;
  }
}
</style>
