<script setup lang="ts">
import { ref } from 'vue'
import { createResource } from 'frappe-ui'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const attendee = ref({
  attendee_name: '',
  attendee_email: '',
  attendee_phone: ''
})

const errorMessage = ref('')

interface AttendeeSession {
  name: string
  access_token: string
  attendee_name: string
  attendee_email: string
  attendee_phone: string
}

type RegistrationResponse = AttendeeSession | { already_registered: true }

function finishRegistration(result: AttendeeSession) {
  localStorage.setItem('event_attendee_id', result.name)
  localStorage.setItem('event_attendee_name', result.attendee_name)
  localStorage.setItem('event_attendee_email', result.attendee_email)
  localStorage.setItem('event_attendee_phone', result.attendee_phone)
  sessionStorage.setItem('event_attendee_id', result.name)
  sessionStorage.setItem('event_attendee_email', result.attendee_email)
  sessionStorage.setItem('event_attendee_access_token', result.access_token)

  const returnTo = route.query.returnTo
  const validReturnPath =
    typeof returnTo === 'string'
    && /^\/(events|event\/|book-ticket\/)/.test(returnTo)

  router.push(validReturnPath ? returnTo : '/events')
}

const registration = createResource({
  url: 'event_management.event_management.doctype.event_attendee.api.register_attendee',

  onSuccess(result: RegistrationResponse) {
    if ('already_registered' in result) {
      router.push('/my-registrations')
      return
    }

    finishRegistration(result)
  },

  onError(error: { messages?: string[] }) {
    errorMessage.value =
      error.messages?.join('\n') || 'Could not save your details. Please try again.'
  }
})

function submitRegistration() {
  errorMessage.value = ''

  const savedAttendeeId = localStorage.getItem('event_attendee_id')
  const sessionAttendeeId = sessionStorage.getItem('event_attendee_id')
  const attendeeAccessToken = sessionStorage.getItem('event_attendee_access_token')
  const savedEmail = localStorage.getItem('event_attendee_email') || ''
  if (
    savedAttendeeId
    && sessionAttendeeId === savedAttendeeId
    && attendeeAccessToken
    && savedEmail.trim().toLowerCase() === attendee.value.attendee_email.trim().toLowerCase()
  ) {
    router.push('/my-registrations')
    return
  }

  registration.submit({
    attendee_name: attendee.value.attendee_name,
    attendee_email: attendee.value.attendee_email,
    attendee_phone: attendee.value.attendee_phone
  })
}
</script>

<template>
  <main class="page">
    <div class="glow glow-one"></div>
    <div class="glow glow-two"></div>

    <div class="wrapper">
      <section class="card">
        <header class="card-header">
          <div class="header-content">
            <div class="brand">EVENT MANAGEMENT</div>
            <div class="header-icon">✦</div>
            <h1>Join the Experience</h1>
            <p>Register your details to explore and book events.</p>
          </div>
          <div class="header-decoration"></div>
        </header>

        <form class="card-body" @submit.prevent="submitRegistration">
          <div class="field">
            <label for="attendee-name">FULL NAME</label>
            <div class="input-wrap">
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="8" r="4" />
                <path d="M4 21c0-4 3.6-7 8-7s8 3 8 7" />
              </svg>
              <input
                id="attendee-name"
                v-model.trim="attendee.attendee_name"
                type="text"
                autocomplete="name"
                placeholder="Your full name"
                required
              />
            </div>
          </div>

          <div class="field">
            <label for="attendee-email">EMAIL ADDRESS</label>
            <div class="input-wrap">
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="5" width="18" height="14" rx="2" />
                <path d="M3 7l9 6 9-6" />
              </svg>
              <input
                id="attendee-email"
                v-model.trim="attendee.attendee_email"
                type="email"
                autocomplete="email"
                placeholder="you@example.com"
                required
              />
            </div>
            <span class="hint">Your ticket will be sent to this address.</span>
          </div>

          <div class="field">
            <label for="attendee-phone">PHONE NUMBER</label>
            <div class="input-wrap">
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z" />
              </svg>
              <input
                id="attendee-phone"
                v-model.trim="attendee.attendee_phone"
                type="tel"
                autocomplete="tel"
                placeholder="+91 98765 43210"
                required
              />
            </div>
          </div>

          <p v-if="errorMessage" role="alert" class="error">
            {{ errorMessage }}
          </p>

          <button class="submit" type="submit" :disabled="registration.loading">
            <span v-if="registration.loading" class="spinner"></span>
            <span v-if="registration.loading">Saving your details...</span>
            <span v-else>Register and view events &nbsp;→</span>
          </button>

          <div class="divider"></div>

          <p class="secure-note">
            🔒 &nbsp;Your details are only used for your event bookings.
          </p>
        </form>
      </section>

      <p class="page-note">Get your entry pass in minutes. See you at the event!</p>
    </div>
  </main>
</template>

<style scoped>
.page {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 18px;
  overflow: hidden;
  background: #f1f3f8;
  font-family: Arial, sans-serif;
  color: #202b43;
}

.glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
  opacity: 0.45;
  pointer-events: none;
}

.glow-one {
  width: 380px;
  height: 380px;
  background: #b8c7ee;
  top: -120px;
  left: -100px;
}

.glow-two {
  width: 340px;
  height: 340px;
  background: #f6d58c;
  bottom: -120px;
  right: -90px;
}

.wrapper {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 520px;
}

.card {
  background: #ffffff;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 15px 45px rgba(25, 40, 75, 0.14);
}

.card-header {
  position: relative;
  overflow: hidden;
  background: linear-gradient(125deg, #182d58, #354e85);
  color: white;
  padding: 36px 38px 42px;
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
  margin-top: 24px;
  font-size: 28px;
  color: #f6d58c;
}

.card-header h1 {
  margin: 10px 0 7px;
  font-size: 30px;
  font-weight: 750;
  color: white;
}

.card-header p {
  margin: 0;
  color: #d7e0f5;
  font-size: 14px;
  line-height: 1.5;
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

.card-body {
  padding: 34px 38px 32px;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field label {
  color: #8791a5;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1.5px;
}

.input-wrap {
  position: relative;
}

.icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 19px;
  height: 19px;
  color: #8791a5;
  transition: color 0.2s;
  pointer-events: none;
}

.input-wrap input {
  width: 100%;
  box-sizing: border-box;
  padding: 14px 14px 14px 44px;
  font-size: 15px;
  color: #26344f;
  background: #f7f8fc;
  border: 1.5px solid #e3e7ef;
  border-radius: 10px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
}

.input-wrap input::placeholder {
  color: #aab2c2;
}

.input-wrap input:hover {
  border-color: #cbd2df;
}

.input-wrap input:focus {
  background: #ffffff;
  border-color: #354e85;
  box-shadow: 0 0 0 4px rgba(53, 78, 133, 0.12);
}

.input-wrap:focus-within .icon {
  color: #354e85;
}

.hint {
  font-size: 12px;
  color: #8993a6;
}

.error {
  margin: 0;
  padding: 12px 14px;
  white-space: pre-line;
  font-size: 13px;
  color: #a33a2a;
  background: #fdecea;
  border: 1px solid #f6c9c3;
  border-radius: 10px;
}

.submit {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 16px;
  border: none;
  border-radius: 10px;
  color: white;
  background: linear-gradient(125deg, #182d58, #354e85);
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(24, 45, 88, 0.25);
  transition: transform 0.15s, box-shadow 0.15s, opacity 0.2s;
}

.submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 12px 26px rgba(24, 45, 88, 0.32);
}

.submit:active:not(:disabled) {
  transform: translateY(0);
}

.submit:disabled {
  opacity: 0.75;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
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

.divider {
  border-top: 1px dashed #cbd2df;
}

.secure-note {
  margin: 0;
  text-align: center;
  font-size: 12px;
  color: #8993a6;
}

.page-note {
  text-align: center;
  color: #8b94a5;
  font-size: 12px;
  margin-top: 20px;
}

@media (max-width: 550px) {
  .page {
    padding: 20px 10px;
  }

  .card-header {
    padding: 28px 24px 32px;
  }

  .card-header h1 {
    font-size: 25px;
  }

  .card-body {
    padding: 26px 22px 24px;
  }
}
</style>
