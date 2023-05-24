frappe.listview_settings['Job Card'] = {
	has_indicator_for_draft: true,
	onload: function(listview) {
                let user=frappe.session.user
                console.log(user,'hello')
               if (user in ['neha@navyacustom.com','pawasthy11@gmail.com','sosowon@navyacustom.com','ksvwon@navyacustom.com']){
                    frappe.set_route("List", "Job Card", "Calendar");
               }

        },

	get_indicator: function(doc) {
		const status_colors = {
			"Work In Progress": "orange",
			"Completed": "green",
			"Cancelled": "red",
			"Material Transferred": "blue",
			"Open": "red",
		};
		const status = doc.status || "Open";
		const color = status_colors[status] || "blue";

		return [__(status), color, `status,=,${status}`];
	}
};

