frappe.listview_settings['Job Card'] = {
	has_indicator_for_draft: true,
	onload: function(listview) {
                let user=frappe.session.user
                console.log(user,'hello')
		let user_all_roles=frappe.user_roles
		let list_super=["Administrator","pawasthy11@gmail.com","amita@navya.biz"]
               if(user_all_roles.includes("Sales Manager") || user_all_roles.includes("Sales Team")){
			if (list_super.includes(user)==false){
				frappe.set_route("List", "Job Card", "Calendar");
			}
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
