
import { createRouter, createWebHistory } from 'vue-router'

export const router = createRouter({
  history: createWebHistory('/event_management'),
  routes: [
    {
      path: '/',
      redirect: '/register'
    },
    {
      path: '/register',
      component: () => import('./pages/Register.vue')
    },
    {
      path: '/events',
      component: () => import('./pages/Home.vue')
    },
    {
      path: '/event/:name',
      component: () => import('./pages/EventDetails.vue')
    },
    {
      path: '/book-ticket/:name',
      component: () => import('./pages/BookTicket.vue')
    },
    {
      path: '/ticket/:name',
      component: () => import('./pages/Ticket.vue')
    },
    {
      path: '/gate-scanner',
      component: () => import('./pages/GateScanner.vue')
    },
    { path: '/dashboard', 
      component: () => import('./pages/Dashboard.vue') 
    },
    {
      path: '/:path(.*)*',
      component: () => import('./pages/NotFound.vue')
    },
    { path: '/checkin-report',
       component: () => import('./pages/CheckinReport.vue') 
    },
    { path: '/my-registrations', 
      component: () => import('./pages/MyRegistrations.vue') },
  ],
})

router.beforeEach((to) => {
  const requiresAttendee = to.path === '/events'
    || to.path.startsWith('/event/')
    || to.path.startsWith('/book-ticket/')
    || to.path.startsWith('/ticket/')

  if (requiresAttendee && !localStorage.getItem('event_attendee_id')) {
    return {
      path: '/register',
      query: { returnTo: to.fullPath }
    }
  }

  return true
})
