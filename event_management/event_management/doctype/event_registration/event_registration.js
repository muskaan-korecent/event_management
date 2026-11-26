// Copyright (c) 2026, Muskaan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Event Registration", {
	refresh(frm) {
		set_event_link_queries(frm);
	},

	event(frm) {
		frm.set_value("ticket_type", null);
		frm.clear_table("addons");
		frm.refresh_field("addons");
		set_event_link_queries(frm);
	},
});

function set_event_link_queries(frm) {
	frm.set_query("ticket_type", () => {
		return frm.doc.event
			? { filters: { event: frm.doc.event } }
			: { filters: { name: ["in", []] } };
	});

	frm.set_query("addon", "addons", (doc) => {
		return doc.event
			? { filters: { event: doc.event } }
			: { filters: { name: ["in", []] } };
	});
}
