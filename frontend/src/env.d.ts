interface Window {
  /**
   * The logged-in user, from the boot data in `www/event_management.py`. Only a
   * production build has boot data. The dev server serves the page without
   * Frappe.
   */
  user?: string
}

declare module '*.vue' {
  import type { DefineComponent } from 'vue'

  const component: DefineComponent<{}, {}, any>
  export default component
}