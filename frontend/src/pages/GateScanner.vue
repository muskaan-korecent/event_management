
<script setup lang="ts">
import { ref, onBeforeUnmount } from 'vue'
import { createResource } from 'frappe-ui'
import { Html5Qrcode } from 'html5-qrcode'

interface AttendeeDetails {
  success: boolean
  message: string
  attendee_name: string
  attendee_email: string
  registration_id: string
  event: string
  ticket_type: string
  payment_status: string
  registration_status: string
  checkin_time: string | null
}

const cameraStarted = ref(false)
const loading = ref(false)
const message = ref('Click Start Camera to scan tickets.')
const messageType = ref('info')
const attendee = ref<AttendeeDetails | null>(null)
const manualSearchText = ref('')
const manualSearchLoading = ref(false)
const manualCheckLoading = ref('')
const manualResults = ref<any[]>([])
const manualSearchPerformed = ref(false)

let scanner: Html5Qrcode | null = null

const checkIn = createResource({
  url: 'event_management.event_management.doctype.event_registration.event_registration.check_in_with_qr',

  makeParams(params: { token: string }) {
    return params
  },

  onSuccess(result: AttendeeDetails) {
    loading.value = false
    message.value = result.message
    messageType.value = result.success ? 'success' : 'error'
    attendee.value = result
    stopCamera()
  },

  onError(error: any) {
    loading.value = false
    attendee.value = null
    message.value =
      error?.messages?.[0] || 'Invalid ticket or check-in failed.'
    messageType.value = 'error'
  }
})

const searchAttendees = createResource({
  url: 'event_management.event_management.doctype.event_registration.event_registration.search_attendees_for_checkin',

  makeParams(params: { search_text: string }) {
    return params
  },

  onSuccess(results: any[]) {
    manualSearchLoading.value = false
    manualResults.value = results || []
    manualSearchPerformed.value = true
  },

  onError(error: any) {
    manualSearchLoading.value = false
    manualResults.value = []
    manualSearchPerformed.value = false
    message.value =
      error?.messages?.[0] || 'Unable to search attendees.'
    messageType.value = 'error'
  }
})

const manualCheckIn = createResource({
  url: 'event_management.event_management.doctype.event_registration.event_registration.manual_checkin',

  makeParams(params: { registration_name: string }) {
    return params
  },

  onSuccess(result: string) {
    manualCheckLoading.value = ''
    attendee.value = null
    message.value = result
    messageType.value = 'success'
    stopCamera()
    searchAttendees.submit({ search_text: manualSearchText.value.trim() })
  },

  onError(error: any) {
    manualCheckLoading.value = ''
    message.value =
      error?.messages?.[0] || 'Manual check-in failed.'
    messageType.value = 'error'
  }
})

async function handleScan(decodedText: string) {
  if (loading.value) return

  loading.value = true
  attendee.value = null
  message.value = 'Verifying ticket...'
  messageType.value = 'info'

  await checkIn.submit({ token: decodedText })
}

async function handleManualSearch() {
  const searchText = manualSearchText.value.trim()
  if (searchText.length < 2) {
    manualResults.value = []
    manualSearchPerformed.value = false
    message.value = 'Enter at least 2 characters to search attendees.'
    messageType.value = 'error'
    return
  }

  manualSearchLoading.value = true
  await searchAttendees.submit({ search_text: searchText })
}

async function handleManualCheckIn(registrationName: string) {
  if (manualCheckLoading.value) return

  manualCheckLoading.value = registrationName
  attendee.value = null
  message.value = 'Checking in attendee...'
  messageType.value = 'info'

  await manualCheckIn.submit({ registration_name: registrationName })
}

async function startCamera() {
  try {
    attendee.value = null
    message.value = 'Starting camera...'
    messageType.value = 'info'

    if (!scanner) {
      scanner = new Html5Qrcode('qr-reader')
    }

    await scanner.start(
      { facingMode: 'environment' },
      {
        fps: 10,
        qrbox: { width: 250, height: 250 }
      },
      handleScan,
      () => {}
    )

    cameraStarted.value = true
    message.value = 'Camera started. Scan an attendee QR code.'
  } catch (error) {
    message.value =
      'Unable to start camera. Please allow camera permission and try again.'
    messageType.value = 'error'
    console.error(error)
  }
}

async function stopCamera() {
  if (scanner && cameraStarted.value) {
    try {
      await scanner.stop()
      await scanner.clear()
    } catch (error) {
      console.error(error)
    }
  }

  cameraStarted.value = false
}

onBeforeUnmount(() => {
  if (scanner && cameraStarted.value) {
    scanner.stop().catch(console.error)
  }
})
</script>

<template>
  <main class="scanner-page">
    <div class="scanner-card">

      <header class="page-header">
        <div class="scanner-icon">▦</div>
        <h1>Gate Check-in Scanner</h1>
        <p>Scan attendee QR tickets to verify and check them in.</p>
      </header>

      <section class="camera-section">

        <div class="manual-checkin">
          <h2>Manual Check-in</h2>
          <p>Search by attendee name or email.</p>

          <form class="manual-search" @submit.prevent="handleManualSearch">
            <input
              v-model="manualSearchText"
              type="search"
              placeholder="Attendee name or email"
              autocomplete="off"
            >
            <button
              type="submit"
              class="search-button"
              :disabled="manualSearchLoading || manualSearchText.trim().length < 2"
            >
              {{ manualSearchLoading ? 'Searching...' : 'Search' }}
            </button>
          </form>

          <div v-if="manualResults.length" class="manual-results">
            <div
              v-for="registration in manualResults"
              :key="registration.name"
              class="manual-result"
            >
              <div class="manual-result-details">
                <strong>{{ registration.attendee_name || 'Unknown attendee' }}</strong>
                <span>{{ registration.attendee_email || '-' }}</span>
                <small>
                  {{ registration.registration_status }}
                  · {{ registration.payment_status }}
                  · {{ registration.name }}
                </small>
              </div>

              <button
                class="manual-check-button"
                :disabled="
                  registration.registration_status !== 'Confirmed'
                  || !!manualCheckLoading
                "
                @click="handleManualCheckIn(registration.name)"
              >
                {{
                  manualCheckLoading === registration.name
                    ? 'Checking in...'
                    : registration.registration_status === 'Checked In'
                      ? 'Checked In'
                      : 'Check In'
                }}
              </button>
            </div>
          </div>
          <p
            v-else-if="manualSearchLoading"
            class="manual-empty"
          >
            Searching...
          </p>
          <p
            v-else-if="manualSearchPerformed"
            class="manual-empty"
          >
            No matching attendees found.
          </p>
        </div>

        <div class="camera-buttons">
          <button
            class="start-button"
            :disabled="cameraStarted || loading"
            @click="startCamera"
          >
            Start Camera
          </button>

          <button
            class="stop-button"
            :disabled="!cameraStarted"
            @click="stopCamera"
          >
            Stop Camera
          </button>
        </div>

        <div id="qr-reader"></div>

        <div class="result-message" :class="messageType">
          {{ message }}
        </div>

        <!-- ATTENDEE DETAILS -->
        <div v-if="attendee" class="attendee-card">

          <div class="attendee-header">
            <div class="success-icon">
              {{ attendee.success ? '✓' : '!' }}
            </div>

            <div>
              <h2>{{ attendee.success ? 'Check-in Successful' : 'Already Checked In' }}</h2>
              <p>{{ attendee.message }}</p>
            </div>
          </div>

          <div class="attendee-info">
            <h3>Attendee Details</h3>

            <div class="detail-row">
              <span>Attendee Name</span>
              <strong>{{ attendee.attendee_name }}</strong>
            </div>

            <div class="detail-row">
              <span>Email Address</span>
              <strong>{{ attendee.attendee_email }}</strong>
            </div>

            <div class="detail-row">
              <span>Registration ID</span>
              <strong>{{ attendee.registration_id }}</strong>
            </div>

            <div class="detail-row">
              <span>Event</span>
              <strong>{{ attendee.event }}</strong>
            </div>

            <div class="detail-row">
              <span>Ticket Type</span>
              <strong>{{ attendee.ticket_type }}</strong>
            </div>

            <div class="detail-row">
              <span>Payment Status</span>
              <strong class="paid">{{ attendee.payment_status }}</strong>
            </div>

            <div class="detail-row">
              <span>Registration Status</span>
              <strong class="checked-in">{{ attendee.registration_status }}</strong>
            </div>

            <div class="detail-row">
              <span>Check-in Time</span>
              <strong>
                {{ attendee.checkin_time
                  ? new Date(attendee.checkin_time).toLocaleString()
                  : 'Not available' }}
              </strong>
            </div>
          </div>

        </div>

      </section>

    </div>
  </main>
</template>

<style scoped>
.scanner-page {
  min-height: 100vh;
  background: #f4f6fa;
  padding: 45px 20px;
  font-family: Arial, sans-serif;
}

.scanner-card {
  max-width: 720px;
  margin: auto;
  padding: 35px;
  background: white;
  border-radius: 18px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.07);
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.scanner-icon {
  font-size: 40px;
  color: #2864e8;
}

.page-header h1 {
  font-size: 28px;
  color: #1e2d4d;
  margin: 12px 0;
}

.page-header p {
  color: #718096;
}

.camera-buttons {
  display: flex;
  justify-content: center;
  gap: 14px;
  margin-bottom: 25px;
}

.manual-checkin {
  margin-bottom: 28px;
  padding: 20px;
  border: 1px solid #dfe6f2;
  border-radius: 12px;
  background: #fbfcff;
}

.manual-checkin h2 {
  margin: 0 0 5px;
  color: #1e2d4d;
  font-size: 18px;
}

.manual-checkin p {
  margin: 0 0 14px;
  color: #718096;
  font-size: 13px;
}

.manual-search {
  display: flex;
  gap: 10px;
}

.manual-search input {
  min-width: 0;
  flex: 1;
  padding: 12px 14px;
  border: 1px solid #ccd6e5;
  border-radius: 8px;
  font-size: 14px;
}

.search-button,
.manual-check-button {
  background: #2864e8;
  color: white;
  white-space: nowrap;
}

.manual-results {
  display: grid;
  gap: 10px;
  margin-top: 14px;
}

.manual-result {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px;
  border: 1px solid #edf0f4;
  border-radius: 8px;
  background: white;
}

.manual-result-details {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
  color: #26344f;
  font-size: 14px;
}

.manual-result-details span,
.manual-result-details small {
  color: #718096;
  overflow-wrap: anywhere;
}

.manual-check-button {
  padding: 10px 14px;
  font-size: 13px;
}

.manual-empty {
  margin: 14px 0 0 !important;
  text-align: center;
}

button {
  padding: 13px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.start-button {
  background: #2864e8;
  color: white;
}

.stop-button {
  background: #e5e7eb;
  color: #26344f;
}

#qr-reader {
  width: 100%;
  max-width: 500px;
  margin: auto;
}

.result-message {
  margin-top: 25px;
  padding: 16px;
  border-radius: 9px;
  text-align: center;
  font-size: 14px;
}

.info {
  background: #eff4ff;
  color: #2855a0;
}

.success {
  background: #e5f7ec;
  color: #18764a;
}

.error {
  background: #fff0f0;
  color: #bd3030;
}

.attendee-card {
  margin-top: 25px;
  border: 1px solid #dce8df;
  border-radius: 14px;
  overflow: hidden;
  background: #fff;
}

.attendee-header {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 22px;
  background: #eaf8ef;
}

.success-icon {
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #18864b;
  color: white;
  border-radius: 50%;
  font-size: 23px;
  font-weight: bold;
}

.attendee-header h2 {
  margin: 0 0 5px;
  color: #176c3e;
  font-size: 19px;
}

.attendee-header p {
  margin: 0;
  color: #47765a;
  font-size: 13px;
}

.attendee-info {
  padding: 22px;
}

.attendee-info h3 {
  margin: 0 0 18px;
  color: #1e2d4d;
  font-size: 17px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  gap: 15px;
  padding: 12px 0;
  border-bottom: 1px solid #edf0f4;
  font-size: 14px;
}

.detail-row span {
  color: #718096;
}

.detail-row strong {
  color: #26344f;
  text-align: right;
  overflow-wrap: anywhere;
}

.detail-row .paid,
.detail-row .checked-in {
  color: #18864b;
}

@media (max-width: 550px) {
  .scanner-card {
    padding: 22px 15px;
  }

  .camera-buttons {
    flex-wrap: wrap;
  }

  .manual-search,
  .manual-result {
    flex-direction: column;
  }

  .manual-search input,
  .manual-search button,
  .manual-check-button {
    width: 100%;
  }

  .detail-row {
    flex-direction: column;
    gap: 5px;
  }

  .detail-row strong {
    text-align: left;
  }
}
</style>
