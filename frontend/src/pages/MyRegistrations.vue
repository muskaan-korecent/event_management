<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { createResource } from 'frappe-ui'
import { useRouter } from 'vue-router'

const attendeeId = sessionStorage.getItem('event_attendee_id')
  || localStorage.getItem('event_attendee_id')
const attendeeAccessToken = sessionStorage.getItem('event_attendee_access_token')
const sessionAttendeeEmail = (sessionStorage.getItem('event_attendee_email') || '')
  .trim()
  .toLowerCase()
const hasLocalAttendeeProfile = Boolean(
  localStorage.getItem('event_attendee_id')
  && localStorage.getItem('event_attendee_email')
)
const usingAttendeeSession = Boolean(attendeeId && attendeeAccessToken)

const registrations = createResource({
  url: usingAttendeeSession
    ? 'event_management.event_management.doctype.event_attendee.api.get_attendee_registrations'
    : 'event_management.event_management.doctype.event_registration.event_registration.get_my_registrations',
  params: usingAttendeeSession
    ? { attendee: attendeeId, access_token: attendeeAccessToken }
    : {},
  auto: !(hasLocalAttendeeProfile && !usingAttendeeSession),
})

const router = useRouter()
const localRegistrations = ref([])
const usingLocalTickets = ref(hasLocalAttendeeProfile && !usingAttendeeSession)
const localTicketsLoading = ref(false)
const localTicketsError = ref('')
const registrationError = ref('')
const cancellingRegistration = ref('')
const displayedRegistrations = computed(() => {
  if (usingLocalTickets.value) {
    return localRegistrations.value
  }

  const items = registrations.data || []
  if (!usingAttendeeSession) {
    return items
  }

  return items.filter(item =>
    item.attendee_email?.trim().toLowerCase() === sessionAttendeeEmail
  )
})
const loading = computed(() =>
  registrations.loading || localTicketsLoading.value
)

const cancelResource = createResource({
  url: 'event_management.event_management.doctype.event_registration.event_registration.cancel_my_registration',

  onSuccess(result) {
    alert(result.message)
    if (usingLocalTickets.value) {
      sessionStorage.removeItem(
        `event_ticket_access_${cancellingRegistration.value}`
      )
      cancellingRegistration.value = ''
      loadLocalTickets()
    } else {
      registrations.reload()
    }
  },

  onError(error) {
    alert(error.messages?.join('\n') || 'Could not cancel registration.')
  },
})

async function loadLocalTickets() {
  const attendeeEmail = (
    sessionStorage.getItem('event_attendee_email')
    || localStorage.getItem('event_attendee_email')
    || ''
  )
    .trim()
    .toLowerCase()

  if (!attendeeEmail) {
    localTicketsError.value = 'Register with this browser before viewing saved tickets.'
    return
  }

  usingLocalTickets.value = true
  localTicketsLoading.value = true
  localTicketsError.value = ''

  const prefix = 'event_ticket_access_'
  const savedTickets = Object.keys(sessionStorage)
    .filter(key => key.startsWith(prefix))
    .map(key => ({
      name: key.slice(prefix.length),
      accessToken: sessionStorage.getItem(key) || '',
    }))
    .filter(ticket => ticket.name && ticket.accessToken)

  let failedRequests = 0
  const results = await Promise.all(savedTickets.map(async ticket => {
    const resource = createResource({
      url: 'event_management.event_management.doctype.event_registration.api.get_ticket_details',
      params: {
        registration_name: ticket.name,
        access_token: ticket.accessToken,
      },
    })

    try {
      return await resource.fetch()
    } catch {
      failedRequests += 1
      return null
    }
  }))

  localRegistrations.value = results.filter(item =>
    item && item.attendee_email?.trim().toLowerCase() === attendeeEmail
  )

  if (failedRequests) {
    localTicketsError.value = 'Some saved tickets could not be loaded.'
  }

  localTicketsLoading.value = false
}

watch(
  () => registrations.error,
  error => {
    if (!error || usingLocalTickets.value) return

    const messages = Array.isArray(error.messages) ? error.messages : []
    const guestError = messages.some(message =>
      message.includes('Please log in to view your registrations.')
    )

    if (guestError && !usingAttendeeSession) {
      loadLocalTickets()
    } else {
      registrationError.value = 'Unable to load your registrations. Please refresh and try again.'
    }
  }
)

onMounted(() => {
  if (usingLocalTickets.value) {
    loadLocalTickets()
  }
})

function refreshRegistrations() {
  if (usingLocalTickets.value) {
    loadLocalTickets()
  } else {
    registrationError.value = ''
    registrations.reload()
  }
}

function canViewTicket(item) {
  return item.registration_status !== 'Cancelled'
    && Boolean(
      item.qr_code_token
      || sessionStorage.getItem(`event_ticket_access_${item.name}`)
    )
}

function canCancelRegistration(item) {
  if (['Cancelled', 'Checked In'].includes(item.registration_status)) {
    return false
  }

  return !usingLocalTickets.value
    || Boolean(sessionStorage.getItem(`event_ticket_access_${item.name}`))
}

function viewTicket(item) {
  const accessToken = item.qr_code_token
    || sessionStorage.getItem(`event_ticket_access_${item.name}`)

  if (!accessToken) return

  sessionStorage.setItem(`event_ticket_access_${item.name}`, accessToken)
  router.push(`/ticket/${encodeURIComponent(item.name)}`)
}

function cancelRegistration(item) {
  const confirmed = window.confirm(
    `Are you sure you want to cancel registration ${item.name}?`
  )

  if (!confirmed) return

  cancellingRegistration.value = item.name
  const params = {
    registration_name: item.name,
  }

  if (usingAttendeeSession) {
    params.attendee = attendeeId
    params.access_token = attendeeAccessToken
  } else if (usingLocalTickets.value) {
    params.access_token = sessionStorage.getItem(
      `event_ticket_access_${item.name}`
    )
  }

  cancelResource.submit(params)
}

// Display-only helper for status badges
function statusClass(status) {
  const value = String(status || '').toLowerCase()
  if (['confirmed', 'checked in', 'paid'].includes(value)) return 'badge-green'
  if (['cancelled', 'failed', 'refunded'].includes(value)) return 'badge-red'
  return 'badge-amber'
}
</script>

<template>
  <div class="page">

    <!-- Hero -->
    <header class="hero">
      <div class="header-decoration"></div>

      <div class="hero-inner">
        <div class="topline">
          <div class="logo">
            <span class="logo-icon">✦</span>
            <span class="logo-text">EVENT MANAGEMENT</span>
          </div>

          <button class="btn-glass" :disabled="loading" @click="refreshRegistrations">
            <span v-if="loading" class="spinner-small"></span>
            <span v-else>↻</span>
            &nbsp;Refresh
          </button>
        </div>

        <div class="hero-text">
          <span class="badge-gold">YOUR BOOKINGS</span>
          <h1>My Registrations</h1>
          <p>View your event bookings and tickets.</p>
        </div>
      </div>
    </header>

    <main class="container">

      <!-- Loading -->
      <div v-if="loading" class="message">
        <div class="spinner"></div>
        Loading your registrations...
      </div>

      <!-- Empty -->
      <div v-else-if="displayedRegistrations.length === 0" class="message">
        <div class="empty-icon">🎟️</div>
        <h3>No tickets yet</h3>
        <p>
          {{ usingLocalTickets
            ? 'No saved tickets were found for this email in this browser session.'
            : "You haven't registered for any events yet."
          }}
        </p>
      </div>

      <!-- List -->
      <div v-else class="registration-list">
        <article
          v-for="item in displayedRegistrations"
          :key="item.name"
          class="registration-card"
          :class="{ cancelled: item.registration_status === 'Cancelled' }"
        >
          <div class="card-top">
            <div class="card-title">
              <span class="label">EVENT</span>
              <h2>{{ item.event }}</h2>
            </div>

            <span class="badge" :class="statusClass(item.registration_status)">
              ● {{ item.registration_status }}
            </span>
          </div>

          <div class="divider"></div>

          <div class="details-grid">
            <div class="detail">
              <span class="label">REGISTRATION ID</span>
              <strong>{{ item.name }}</strong>
            </div>

            <div class="detail">
              <span class="label">ATTENDEE</span>
              <strong>{{ item.attendee_name }}</strong>
            </div>

            <div class="detail">
              <span class="label">TICKET TYPE</span>
              <strong>{{ item.ticket_type }}</strong>
            </div>

            <div class="detail">
              <span class="label">PAYMENT STATUS</span>
              <span class="badge small" :class="statusClass(item.payment_status)">
                {{ item.payment_status || '—' }}
              </span>
            </div>

            <div class="detail">
              <span class="label">TOTAL AMOUNT</span>
              <strong class="amount">₹{{ item.total_amount }}</strong>
            </div>
          </div>

          <div class="actions">
            <button
              v-if="canViewTicket(item)"
              class="btn-primary"
              @click="viewTicket(item)"
            >
              View Ticket &nbsp;→
            </button>

            <p
              v-else-if="item.registration_status !== 'Cancelled'"
              class="ticket-unavailable"
            >
              ◷ &nbsp;Ticket access is not available yet.
            </p>

            <button
              v-if="canCancelRegistration(item)"
              class="btn-danger"
              :disabled="cancelResource.loading"
              @click="cancelRegistration(item)"
            >
              {{ cancelResource.loading ? 'Cancelling...' : 'Cancel Registration' }}
            </button>
          </div>

          <p v-if="item.registration_status === 'Cancelled'" class="cancelled-note">
            This registration has been cancelled.
          </p>
        </article>
      </div>

      <p v-if="localTicketsError" role="alert" class="error-box">
        {{ localTicketsError }}
      </p>

      <p v-if="registrationError" role="alert" class="error-box">
        {{ registrationError }}
      </p>

      <div class="explore">
        <button class="btn-gold" @click="router.push('/events')">
          Explore more events &nbsp;→
        </button>
      </div>

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
  max-width: 900px;
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
  max-width: 900px;
  margin: -40px auto 0;
  padding: 0 24px 40px;
  position: relative;
  z-index: 3;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.label {
  display: block;
  color: #8791a5;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1.5px;
}

/* Registration cards */
.registration-list {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.registration-card {
  position: relative;
  overflow: hidden;
  background: #ffffff;
  border-radius: 18px;
  padding: 28px 32px 26px 36px;
  box-shadow: 0 12px 35px rgba(25, 40, 75, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.registration-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 6px;
  background: linear-gradient(180deg, #354e85, #f6d58c);
}

.registration-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 20px 45px rgba(25, 40, 75, 0.16);
}

.registration-card.cancelled {
  opacity: 0.8;
}

.registration-card.cancelled::before {
  background: #d9a79f;
}

.card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
}

.card-title h2 {
  margin: 6px 0 0;
  font-size: 24px;
  font-weight: 750;
  color: #1c315d;
}

.divider {
  border-top: 1px dashed #cbd2df;
  margin: 22px 0;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 22px 20px;
}

.detail {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  min-width: 0;
}

.detail strong {
  color: #26344f;
  font-size: 14px;
  overflow-wrap: anywhere;
}

.amount {
  font-size: 18px !important;
  color: #1c315d !important;
}

/* Badges */
.badge {
  padding: 7px 13px;
  border-radius: 30px;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.badge.small {
  padding: 5px 11px;
}

.badge-green {
  color: #18764a;
  background: #e4f6eb;
}

.badge-amber {
  color: #986817;
  background: #fff2d8;
}

.badge-red {
  color: #a33a2a;
  background: #fdecea;
}

/* Actions */
.actions {
  margin-top: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.ticket-unavailable {
  margin: 0;
  font-size: 13px;
  color: #8993a6;
}

.cancelled-note {
  margin: 20px 0 0;
  padding: 12px 14px;
  font-size: 13px;
  font-weight: 700;
  color: #a33a2a;
  background: #fdecea;
  border-radius: 10px;
}

/* Buttons */
.btn-primary {
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  color: #ffffff;
  background: linear-gradient(125deg, #182d58, #354e85);
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(24, 45, 88, 0.22);
  transition: transform 0.15s, box-shadow 0.15s;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 26px rgba(24, 45, 88, 0.3);
}

.btn-danger {
  padding: 11px 20px;
  border: 1.5px solid #e9b8b0;
  border-radius: 10px;
  color: #a33a2a;
  background: #ffffff;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-danger:hover:not(:disabled) {
  background: #fdecea;
}

.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-glass {
  display: inline-flex;
  align-items: center;
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

.btn-glass:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
}

.btn-glass:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.explore {
  text-align: center;
  padding-top: 6px;
}

.btn-gold {
  padding: 15px 32px;
  border: none;
  border-radius: 10px;
  background: #f6d58c;
  color: #182d58;
  font-size: 15px;
  font-weight: 750;
  cursor: pointer;
  box-shadow: 0 8px 22px rgba(24, 45, 88, 0.18);
  transition: transform 0.15s, box-shadow 0.15s;
}

.btn-gold:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(24, 45, 88, 0.26);
}

/* States */
.message {
  background: #ffffff;
  padding: 56px 30px;
  border-radius: 18px;
  text-align: center;
  color: #6b7589;
  box-shadow: 0 12px 35px rgba(25, 40, 75, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.message h3 {
  margin: 0;
  font-size: 20px;
  color: #1c315d;
}

.message p {
  margin: 0;
  max-width: 380px;
  line-height: 1.6;
}

.empty-icon {
  font-size: 46px;
}

.error-box {
  margin: 0;
  padding: 14px 18px;
  font-size: 14px;
  text-align: center;
  color: #a33a2a;
  background: #fdecea;
  border: 1px solid #f6c9c3;
  border-radius: 12px;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #dfe5f2;
  border-top-color: #354e85;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.spinner-small {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
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

@media (max-width: 720px) {
  .details-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 560px) {
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
    padding: 0 12px 30px;
  }

  .registration-card {
    padding: 22px 20px 22px 24px;
  }

  .card-title h2 {
    font-size: 20px;
  }

  .details-grid {
    grid-template-columns: 1fr;
    gap: 18px;
  }

  .actions {
    flex-direction: column;
    align-items: stretch;
  }

  .btn-primary,
  .btn-danger {
    width: 100%;
  }
}
</style>