<script setup>
import { createResource } from 'frappe-ui'
import { computed } from 'vue'

const dashboard = createResource({
  url: 'event_management.event_management.doctype.managed_event.managed_event.get_organizer_dashboard',
  auto: true,
})

const stats = computed(() => dashboard.data || {})

const monthlyTrends = computed(() => {
  return stats.value.monthly_trends || []
})

const maxRegistrations = computed(() => {
  return Math.max(
    1,
    ...monthlyTrends.value.map(item => item.registrations)
  )
})

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount || 0)
}

function formatDate(date) {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('en-IN')
}

// Display-only helpers
function statusClass(status) {
  const value = String(status || '').toLowerCase()
  if (['confirmed', 'checked in', 'paid'].includes(value)) return 'badge-green'
  if (['cancelled', 'failed', 'refunded'].includes(value)) return 'badge-red'
  return 'badge-amber'
}

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

          <button class="btn-glass" :disabled="dashboard.loading" @click="dashboard.reload()">
            <span v-if="dashboard.loading" class="spinner-small"></span>
            <span v-else>↻</span>
            &nbsp;Refresh
          </button>
        </div>

        <div class="hero-text">
          <span class="badge-gold">ORGANIZER</span>
          <h1>Organizer Dashboard</h1>
          <p>Overview of your events and registrations</p>
        </div>
      </div>
    </header>

    <main class="container">

      <div v-if="dashboard.loading" class="message">
        <div class="spinner"></div>
        Loading dashboard...
      </div>

      <div v-else-if="dashboard.error" class="error-box">
        Unable to load dashboard. Please check your login and permissions.
      </div>

      <template v-else>

        <!-- Stats -->
        <div class="stats-grid">

          <div class="stat-card">
            <div class="stat-icon blue">📅</div>
            <span class="label">TOTAL EVENTS</span>
            <h2>{{ stats.total_events || 0 }}</h2>
          </div>

          <div class="stat-card">
            <div class="stat-icon blue">🎟️</div>
            <span class="label">TOTAL REGISTRATIONS</span>
            <h2>{{ stats.total_registrations || 0 }}</h2>
          </div>

          <div class="stat-card">
            <div class="stat-icon green">✔</div>
            <span class="label">CONFIRMED</span>
            <h2>{{ stats.confirmed_registrations || 0 }}</h2>
          </div>

          <div class="stat-card">
            <div class="stat-icon amber">🚪</div>
            <span class="label">CHECKED-IN</span>
            <h2>{{ stats.checked_in || 0 }}</h2>
          </div>

          <div class="stat-card revenue">
            <div class="header-decoration small"></div>
            <div class="stat-icon gold">₹</div>
            <span class="label">TOTAL REVENUE</span>
            <h2>{{ formatCurrency(stats.total_revenue) }}</h2>
          </div>

        </div>

        <!-- Charts -->
        <div class="two-col">

          <section class="card">
            <div class="section-head">
              <span class="label">TRENDS</span>
              <h3>Monthly Registrations</h3>
            </div>

            <div v-if="monthlyTrends.length" class="chart">
              <div
                v-for="item in monthlyTrends"
                :key="item.month"
                class="chart-row"
              >
                <span class="month">{{ item.month }}</span>

                <div class="bar-background">
                  <div
                    class="bar"
                    :style="{
                      width: (item.registrations / maxRegistrations * 100) + '%'
                    }"
                  ></div>
                </div>

                <strong class="chart-value">{{ item.registrations }}</strong>
              </div>
            </div>

            <p v-else class="empty">No registration data available yet.</p>
          </section>

          <section class="card">
            <div class="section-head">
              <span class="label">EARNINGS</span>
              <h3>Monthly Revenue</h3>
            </div>

            <div v-if="monthlyTrends.length" class="revenue-list">
              <div
                v-for="item in monthlyTrends"
                :key="item.month"
                class="revenue-row"
              >
                <span class="month">{{ item.month }}</span>
                <strong>{{ formatCurrency(item.revenue) }}</strong>
              </div>
            </div>

            <p v-else class="empty">No revenue data available yet.</p>
          </section>

        </div>

        <!-- Recent registrations -->
        <section class="card">
          <div class="section-head">
            <span class="label">LATEST ACTIVITY</span>
            <h3>Recent Registrations</h3>
          </div>

          <div v-if="stats.recent_registrations?.length" class="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Attendee</th>
                  <th>Event</th>
                  <th>Registration</th>
                  <th>Payment</th>
                  <th>Date</th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="registration in stats.recent_registrations"
                  :key="registration.name"
                >
                  <td>
                    <div class="person">
                      <span class="avatar">{{ initial(registration.attendee_name) }}</span>
                      <div class="person-info">
                        <strong>{{ registration.attendee_name }}</strong>
                        <small>{{ registration.attendee_email }}</small>
                      </div>
                    </div>
                  </td>
                  <td class="event-cell">{{ registration.event }}</td>
                  <td>
                    <span class="badge" :class="statusClass(registration.registration_status)">
                      ● {{ registration.registration_status }}
                    </span>
                  </td>
                  <td>
                    <span class="badge" :class="statusClass(registration.payment_status)">
                      {{ registration.payment_status || '—' }}
                    </span>
                  </td>
                  <td class="date-cell">{{ formatDate(registration.creation) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <p v-else class="empty">No registrations found.</p>
        </section>

      </template>
    </main>

    <footer class="footer">Built on Frappe</footer>
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
  padding-bottom: 80px;
}

.hero-inner {
  position: relative;
  z-index: 2;
  max-width: 1160px;
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
  max-width: 1160px;
  margin: -50px auto 0;
  padding: 0 24px 40px;
  position: relative;
  z-index: 3;
  display: flex;
  flex-direction: column;
  gap: 26px;
}

.label {
  display: block;
  color: #8791a5;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1.5px;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
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
}

.stat-icon.gold {
  background: #f6d58c;
  color: #182d58;
}

.stat-card h2 {
  margin: 8px 0 0;
  font-size: 30px;
  font-weight: 750;
  color: #1c315d;
}

.stat-card.revenue {
  background: linear-gradient(125deg, #182d58, #354e85);
}

.stat-card.revenue .label {
  color: #c5d4f5;
}

.stat-card.revenue h2 {
  color: #f6d58c;
  font-size: 26px;
}

/* Cards */
.card {
  background: #ffffff;
  border-radius: 18px;
  padding: 28px 30px;
  box-shadow: 0 12px 35px rgba(25, 40, 75, 0.1);
}

.two-col {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: 26px;
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

/* Chart */
.chart {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chart-row {
  display: flex;
  align-items: center;
  gap: 14px;
}

.month {
  width: 80px;
  flex-shrink: 0;
  font-size: 13px;
  font-weight: 600;
  color: #5c667b;
}

.bar-background {
  flex: 1;
  height: 14px;
  background: #eef1f7;
  border-radius: 10px;
  overflow: hidden;
}

.bar {
  height: 100%;
  min-width: 4px;
  background: linear-gradient(90deg, #354e85, #6f8bd1);
  border-radius: 10px;
  transition: width 0.6s ease;
}

.chart-value {
  min-width: 28px;
  text-align: right;
  font-size: 14px;
  color: #1c315d;
}

.revenue-list {
  display: flex;
  flex-direction: column;
}

.revenue-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 13px 0;
  border-bottom: 1px dashed #cbd2df;
}

.revenue-row:last-child {
  border-bottom: none;
}

.revenue-row strong {
  font-size: 15px;
  color: #18764a;
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

.badge-red {
  color: #a33a2a;
  background: #fdecea;
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

.empty {
  margin: 0;
  color: #8993a6;
  font-size: 14px;
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

@media (max-width: 1050px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 860px) {
  .two-col {
    grid-template-columns: 1fr;
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

  .stats-grid {
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-card h2 {
    font-size: 24px;
  }

  .card {
    padding: 22px 18px;
  }

  .month {
    width: 64px;
  }
}
</style>