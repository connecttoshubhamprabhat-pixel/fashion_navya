// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.views.calendar["Material Request"] = {
	field_map: {
		"start": "schedule_date",
		"end": "schedule_date",
		"id": "name",
		"title": "customer",
		"allDay": "allDay"
	},
	gantt: true,
	filters: [
		{
			"fieldtype": "Link",
			"fieldname": "customer",
			"options": "Customer",
			"label": __("Customer")
		},
		{
			"fieldtype": "Select",
			"fieldname": "status",
			"options": "Pending\nDraft\nTransferred\nManufactured\nStopped",
			"label": __("MR Status")
		},
		{
			"fieldtype": "Select",
			"fieldname": "purpose",
			"options": "Manufacture\nMaterial Transfer\nPurchase\nMaterial Issue",
			"label": __("Material Request Type")
		},
	],
	get_events_method: "fashion_navya.utils.doc_event.mr.get_events_mr",
	get_css_class: function(data) {
		if(data.status=="Manufactured") {
			return "success";
		} if(data.status=="Pending") {
			return "danger";
		} else if(data.status=="Draft") {
			return "warning";
		} else if(data.status=="Transferred") {
			return "success";
		}
	}
}
