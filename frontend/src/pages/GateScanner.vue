
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

async function handleScan(decodedText: string) {
  if (loading.value) return

  loading.value = true
  attendee.value = null
  message.value = 'Verifying ticket...'
  messageType.value = 'info'

  await checkIn.submit({ token: decodedText })
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

  .detail-row {
    flex-direction: column;
    gap: 5px;
  }

  .detail-row strong {
    text-align: left;
  }
}
</style>
