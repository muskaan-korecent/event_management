<script setup>
import { createResource } from 'frappe-ui'
import { computed, ref, watch } from 'vue'

const selectedEvent = ref('')

const report = createResource({
  url: 'event_management.event_management.doctype.managed_event.managed_event.get_organizer_checkin_report',
  auto: true,
})

const data = computed(() => report.data || {})

watch(selectedEvent, (event) => {
  report.reload(event ? { event } : {})
})

function formatDate(value) {
  if (!value) return '-'

  return new Date(value).toLocaleString('en-IN')
}

function exportAttendees() {
  const attendees = data.value.attendees || []

  if (!attendees.length) {
    alert('No attendees available to export.')
    return
  }

  const headers = ['name', 'email']

  const rows = attendees.map(item => [
    item.attendee_name,
    item.attendee_email,
  ])

  const csv = [headers, ...rows]
    .map(row =>
      row.map(value =>
        `"${String(value ?? '').replace(/"/g, '""')}"`
      ).join(',')
    )
    .join('\n')

  const blob = new Blob(['\uFEFF' + csv], {
    type: 'text/csv;charset=utf-8;',
  })

  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = url
  link.download = 'event-attendees.csv'
  link.click()

  URL.revokeObjectURL(url)
}

// Display-only helper
function initial(name) {
  return String(name || '?').trim().charAt(0).toUpperCase() || '?'
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

          <div class="header-actions">
            <button
              class="btn-glass"
              :disabled="report.loading"
              @click="report.reload(selectedEvent ? { event: selectedEvent } : {})"
            >
              <span v-if="report.loading" class="spinner-small"></span>
              <span v-else>↻</span>
              &nbsp;Refresh
            </button>

            <button class="btn-gold" @click="exportAttendees">
              ↓ &nbsp;Export CSV
            </button>
          </div>
        </div>

        <div class="hero-text">
          <span class="badge-gold">ORGANIZER</span>
          <h1>Check-in Report</h1>
          <p>Track attendee arrivals and event attendance.</p>
        </div>
      </div>
    </header>

    <main class="container">

      <!-- Filter -->
      <section class="filter-card">
        <label for="event" class="label">FILTER BY EVENT</label>

        <div class="select-wrap">
          <select id="event" v-model="selectedEvent">
            <option value="">All My Events</option>
            <option
              v-for="event in data.events || []"
              :key="event.name"
              :value="event.name"
            >
              {{ event.event_title }}
            </option>
          </select>
          <span class="select-arrow">▾</span>
        </div>
      </section>

      <div v-if="report.loading" class="message">
        <div class="spinner"></div>
        Loading check-in report...
      </div>

      <div v-else-if="report.error" class="error-box">
        Unable to load report. Please check your login and permissions.
      </div>

      <template v-else>

        <!-- Stats -->
        <div class="stats-grid">

          <div class="stat-card">
            <div class="stat-icon blue">🎟️</div>
            <span class="label">TOTAL REGISTRATIONS</span>
            <h2>{{ data.total_registrations || 0 }}</h2>
          </div>

          <div class="stat-card">
            <div class="stat-icon green">✔</div>
            <span class="label">CHECKED IN</span>
            <h2 class="green-text">{{ data.checked_in || 0 }}</h2>
          </div>

          <div class="stat-card">
            <div class="stat-icon amber">◷</div>
            <span class="label">NOT CHECKED IN</span>
            <h2 class="amber-text">{{ data.not_checked_in || 0 }}</h2>
          </div>

          <div class="stat-card attendance">
            <div class="header-decoration small"></div>
            <div class="attendance-content">
              <div>
                <span class="label">ATTENDANCE</span>
                <h2>{{ data.attendance_percentage || 0 }}%</h2>
              </div>

              <div
                class="ring"
                :style="{
                  background: `conic-gradient(#f6d58c ${Number(data.attendance_percentage || 0) * 3.6}deg, rgba(255,255,255,0.18) 0deg)`
                }"
              >
                <span class="ring-inner">✦</span>
              </div>
            </div>
          </div>

        </div>

        <!-- Attendee table -->
        <section class="card">
          <div class="section-head">
            <span class="label">ATTENDEES</span>
            <h3>Attendee Details</h3>
          </div>

          <div v-if="data.attendees?.length" class="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Attendee</th>
                  <th>Event</th>
                  <th>Status</th>
                  <th>Check-in Time</th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="attendee in data.attendees"
                  :key="attendee.name"
                >
                  <td>
                    <div class="person">
                      <span class="avatar">{{ initial(attendee.attendee_name) }}</span>
                      <div class="person-info">
                        <strong>{{ attendee.attendee_name }}</strong>
                        <small>{{ attendee.attendee_email }}</small>
                      </div>
                    </div>
                  </td>

                  <td class="event-cell">{{ attendee.event }}</td>

                  <td>
                    <span
                      class="badge"
                      :class="attendee.registration_status === 'Checked In'
                        ? 'badge-green'
                        : 'badge-amber'"
                    >
                      ● {{ attendee.registration_status }}
                    </span>
                  </td>

                  <td class="date-cell">{{ formatDate(attendee.checkin_time) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-else class="empty-state">
            <div class="empty-icon">📋</div>
            <p>No attendee registrations found.</p>
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
  max-width: 1100px;
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

.header-decoration.small {
  width: 150px;
  height: 150px;
  right: -50px;
  top: -60px;
  box-shadow: 0 0 0 18px rgba(255, 255, 255, 0.04);
}

.topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
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

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
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
  max-width: 1100px;
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

/* Filter */
.filter-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  padding: 18px 26px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 12px 35px rgba(25, 40, 75, 0.1);
}

.select-wrap {
  position: relative;
  min-width: 260px;
}

.select-wrap select {
  width: 100%;
  appearance: none;
  padding: 12px 40px 12px 16px;
  font-size: 14px;
  font-weight: 600;
  color: #26344f;
  background: #f7f8fc;
  border: 1.5px solid #e3e7ef;
  border-radius: 10px;
  outline: none;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.select-wrap select:focus {
  border-color: #354e85;
  box-shadow: 0 0 0 4px rgba(53, 78, 133, 0.12);
}

.select-arrow {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #8791a5;
  pointer-events: none;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
}

.stat-card {
  position: relative;
  overflow: hidden;
  padding: 22px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 12px 35px rgba(25, 40, 75, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 45px rgba(25, 40, 75, 0.16);
}

.stat-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 16px;
}

.stat-icon.blue {
  background: #e8edf9;
}

.stat-icon.green {
  background: #e4f6eb;
  color: #18764a;
}

.stat-icon.amber {
  background: #fff2d8;
  color: #986817;
}

.stat-card h2 {
  margin: 8px 0 0;
  font-size: 32px;
  font-weight: 750;
  color: #1c315d;
}

.green-text {
  color: #18764a !important;
}

.amber-text {
  color: #c27b18 !important;
}

.stat-card.attendance {
  background: linear-gradient(125deg, #182d58, #354e85);
}

.attendance .label {
  color: #c5d4f5;
}

.attendance h2 {
  color: #f6d58c;
  margin-top: 14px;
}

.attendance-content {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  height: 100%;
}

.ring {
  width: 64px;
  height: 64px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.ring-inner {
  width: 46px;
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #243c6e;
  color: #f6d58c;
  font-size: 18px;
}

/* Cards */
.card {
  background: #ffffff;
  border-radius: 18px;
  padding: 28px 30px;
  box-shadow: 0 12px 35px rgba(25, 40, 75, 0.1);
}

.section-head {
  margin-bottom: 22px;
}

.section-head h3 {
  margin: 6px 0 0;
  font-size: 22px;
  font-weight: 750;
  color: #1c315d;
}

/* Table */
.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

th {
  padding: 12px 14px;
  text-align: left;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: #8791a5;
  background: #f7f8fc;
  white-space: nowrap;
}

th:first-child {
  border-radius: 10px 0 0 10px;
}

th:last-child {
  border-radius: 0 10px 10px 0;
}

td {
  padding: 14px;
  border-bottom: 1px solid #eef1f7;
  vertical-align: middle;
  color: #3c4963;
}

tbody tr {
  transition: background 0.15s;
}

tbody tr:hover {
  background: #f7f9fe;
}

tbody tr:last-child td {
  border-bottom: none;
}

.person {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 38px;
  height: 38px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: linear-gradient(125deg, #182d58, #354e85);
  color: #f6d58c;
  font-weight: 700;
}

.person-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.person-info strong {
  color: #26344f;
  white-space: nowrap;
}

.person-info small {
  color: #8993a6;
  font-size: 12px;
}

.event-cell {
  font-weight: 600;
  color: #1c315d;
}

.date-cell {
  white-space: nowrap;
  color: #7b8495;
}

/* Badges */
.badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 30px;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.badge-green {
  color: #18764a;
  background: #e4f6eb;
}

.badge-amber {
  color: #986817;
  background: #fff2d8;
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

.btn-gold {
  padding: 10px 20px;
  border: none;
  border-radius: 9px;
  background: #f6d58c;
  color: #182d58;
  font-size: 14px;
  font-weight: 750;
  cursor: pointer;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.18);
  transition: transform 0.15s, box-shadow 0.15s;
}

.btn-gold:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.25);
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
  gap: 14px;
}

.error-box {
  padding: 22px;
  text-align: center;
  color: #a33a2a;
  background: #fdecea;
  border: 1px solid #f6c9c3;
  border-radius: 16px;
}

.empty-state {
  padding: 30px 0 10px;
  text-align: center;
  color: #8993a6;
}

.empty-state p {
  margin: 8px 0 0;
  font-size: 14px;
}

.empty-icon {
  font-size: 40px;
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
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 600px) {
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

  .filter-card {
    flex-direction: column;
    align-items: stretch;
  }

  .select-wrap {
    min-width: 0;
  }

  .stats-grid {
    gap: 12px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-card h2 {
    font-size: 26px;
  }

  .ring {
    width: 52px;
    height: 52px;
  }

  .ring-inner {
    width: 36px;
    height: 36px;
    font-size: 14px;
  }

  .card {
    padding: 22px 18px;
  }
}
</style>