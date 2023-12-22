frappe.views.calendar["Material Request"] = {
	field_map: {
		"due_date": "schedule_date",
		"id": "name",
		"color": "color",
		"title":"subject",
		"status": "status"
	},
	gantt: {
		field_map: {
			"id": "name",
			"due_date": "due_date",
			"color": "color",
			"title":"subject",
			"status": "status"
		}
	},


	get_events_method: "fashion_navya.utils.doc_event.mr.get_mr_details"
};

