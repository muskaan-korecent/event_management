<script setup lang="ts">
import { computed } from 'vue'
import { createResource } from 'frappe-ui'
import { useRouter } from 'vue-router'

const router = useRouter()

interface Event {
  name: string
  event_title: string
  description?: string
  venue?: string
  start_date?: string
  start_time?: string
  cover_image?: string
}

const events = createResource({
  url: 'event_management.event_management.doctype.managed_event.managed_event.get_published_events',
  auto: true
})

const eventList = computed(() => (events.data || []) as Event[])
const eventsError = computed(() => {
  const error = events.error
  return error instanceof Error ? error.message : 'Unable to load events.'
})

function formatDate(date?: string) {
  if (!date) return 'Date not announced'

  return new Date(`${date}T00:00:00`).toLocaleDateString(
    'en-IN',
    {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    }
  )
}

function openEvent(event: Event) {
  router.push(`/event/${encodeURIComponent(event.name)}`)
}
</script>

<template>
  <div class="page">

    <!-- Hero header -->
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
            :disabled="events.loading"
            @click="events.reload()"
          >
            <span v-if="events.loading" class="spinner-small"></span>
            <span v-else>↻</span>
            &nbsp;Refresh Events
          </button>
        </div>

        <div class="hero-text">
          <span class="badge-gold">DISCOVER</span>
          <h1>Upcoming Events</h1>
          <p>Explore our published events and find something you'll love.</p>
        </div>
      </div>
    </header>

    <main class="container">

      <!-- Loading -->
      <div v-if="events.loading" class="message">
        <div class="spinner"></div>
        Loading events...
      </div>

      <!-- Error -->
      <div v-else-if="events.error" class="error-box">
        <p>{{ eventsError }}</p>
        <button class="btn-outline" @click="events.reload()">Try Again</button>
      </div>

      <!-- No events -->
      <div v-else-if="eventList.length === 0" class="message">
        <div class="empty-icon">🎉</div>
        <h3>No published events yet</h3>
        <p>Please check back later for upcoming events.</p>
      </div>

      <!-- Event cards -->
      <div v-else class="grid">
        <article
          v-for="event in eventList"
          :key="event.name"
          class="event-card"
          @click="openEvent(event)"
        >

          <div class="cover">
            <img
              v-if="event.cover_image"
              :src="event.cover_image"
              :alt="event.event_title"
            />
            <div v-else class="cover-fallback">
              <div class="fallback-ring"></div>
              <span>✦</span>
            </div>

            <div class="cover-overlay"></div>
            <span class="badge-live">● Published</span>
          </div>

          <div class="card-body">
            <h3>{{ event.event_title }}</h3>

            <p class="description">
              {{ event.description?.replace(/<[^>]*>/g, '').trim() || 'No description available.' }}
            </p>

            <div class="meta">
              <div class="meta-row">
                <span class="meta-icon">📅</span>
                <span>{{ formatDate(event.start_date) }}</span>
              </div>

              <div v-if="event.start_time" class="meta-row">
                <span class="meta-icon">🕒</span>
                <span>{{ event.start_time }}</span>
              </div>

              <div v-if="event.venue" class="meta-row">
                <span class="meta-icon">📍</span>
                <span>{{ event.venue }}</span>
              </div>
            </div>

            <div class="card-footer">
              <span>View Event Details</span>
              <span class="arrow">→</span>
            </div>
          </div>

        </article>
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
  max-width: 1120px;
  margin: auto;
  padding: 22px 24px 0;
}

.header-decoration {
  position: absolute;
  width: 320px;
  height: 320px;
  right: -90px;
  top: -130px;
  border: 1px solid rgba(255, 255, 255, 0.17);
  border-radius: 50%;
  box-shadow: 0 0 0 36px rgba(255, 255, 255, 0.04),
              0 0 0 76px rgba(255, 255, 255, 0.035);
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
  color: #ffffff;
}

.hero-text {
  margin-top: 50px;
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
  margin: 16px 0 10px;
  font-size: 42px;
  font-weight: 750;
  color: #ffffff;
}

.hero-text p {
  margin: 0;
  font-size: 16px;
  color: #d7e0f5;
}

/* Container */
.container {
  max-width: 1120px;
  margin: -40px auto 0;
  padding: 0 24px 50px;
  position: relative;
  z-index: 3;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 26px;
}

/* Event card */
.event-card {
  background: #ffffff;
  border-radius: 18px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 12px 35px rgba(25, 40, 75, 0.12);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
}

.event-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 22px 50px rgba(25, 40, 75, 0.2);
}

.cover {
  position: relative;
  height: 190px;
  overflow: hidden;
  background: #182d58;
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.4s;
}

.event-card:hover .cover img {
  transform: scale(1.06);
}

.cover-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(24, 45, 88, 0.05) 40%, rgba(24, 45, 88, 0.5));
  pointer-events: none;
}

.cover-fallback {
  position: relative;
  height: 100%;
  background: linear-gradient(125deg, #182d58, #354e85);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 46px;
  color: #f6d58c;
  overflow: hidden;
}

.fallback-ring {
  position: absolute;
  width: 190px;
  height: 190px;
  right: -50px;
  top: -70px;
  border: 1px solid rgba(255, 255, 255, 0.17);
  border-radius: 50%;
  box-shadow: 0 0 0 22px rgba(255, 255, 255, 0.04);
}

.badge-live {
  position: absolute;
  top: 14px;
  left: 14px;
  z-index: 2;
  padding: 6px 12px;
  border-radius: 30px;
  font-size: 11px;
  font-weight: 700;
  color: #18764a;
  background: #e4f6eb;
}

.card-body {
  padding: 22px 24px 20px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.card-body h3 {
  margin: 0 0 10px;
  font-size: 20px;
  font-weight: 750;
  color: #1c315d;
  line-height: 1.3;
}

.description {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #7b8495;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px dashed #cbd2df;
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  font-weight: 600;
  color: #3c4963;
}

.meta-icon {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: #eef1f7;
  font-size: 13px;
  flex-shrink: 0;
}

.card-footer {
  margin-top: 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  font-weight: 700;
  color: #354e85;
}

.arrow {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #eef1f7;
  transition: background 0.2s, color 0.2s, transform 0.2s;
}

.event-card:hover .arrow {
  background: #354e85;
  color: #ffffff;
  transform: translateX(3px);
}

/* Buttons */
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

.btn-outline {
  margin-top: 14px;
  padding: 10px 18px;
  border: 1px solid #354e85;
  border-radius: 9px;
  background: #ffffff;
  color: #354e85;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.btn-outline:hover {
  background: #f0f3fb;
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
}

.empty-icon {
  font-size: 46px;
}

.error-box {
  padding: 24px;
  color: #a33a2a;
  background: #fdecea;
  border: 1px solid #f6c9c3;
  border-radius: 16px;
}

.error-box p {
  margin: 0;
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

@media (max-width: 960px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
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
    margin-top: 36px;
  }

  .hero-text h1 {
    font-size: 30px;
  }

  .container {
    padding: 0 12px 40px;
  }

  .grid {
    grid-template-columns: 1fr;
  }

  .btn-glass {
    padding: 9px 12px;
    font-size: 13px;
  }
}
</style>