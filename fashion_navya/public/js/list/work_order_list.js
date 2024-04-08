frappe.listview_settings['Work Order'] = {
	add_fields: ["bom_no", "status", "sales_order", "qty",
		"produced_qty", "expected_delivery_date", "planned_start_date", "planned_end_date"],
	filters: [["status", "!=", "Stopped"]],
	onload: function(listview) {
		let user=frappe.session.user
		let libberheri_users=['anchala@example.com','akansha@example.com','pawasthy11@gmail.coma']
		let user_list=['pawasthy11@gmail.com','neha@navyacustom.com','sosowon@navyacustom.com','ksvwon@navyacustom.com']
		// let user_all_roles=frappe.user_roles
		// 	if(user_all_roles.includes("Sales Manager") || user_all_roles.includes("Sales Team")){
		// 				frappe.set_route("List", "Work Order", "Calendar");
    //            }
			if (user_list.includes(user)){
				console.log('a')
			//	frappe.route_options = {"sales_order":["is","set"]};
			//	frappe.set_route("List", "Work Order");

			}
			if (libberheri_users.includes(user)){
				console.log('a')
			frappe.route_options = {"fg_warehouse":["=","Libberhedi finished Products - NAVYA"]};
			frappe.set_route("List", "Work Order");

			}

			

	},
	get_indicator: function(doc) {
		if(doc.status==="Submitted") {
			return [__("Not Started"), "orange", "status,=,Submitted"];
		} else {
			return [__(doc.status), {
				"Draft": "red",
				"Stopped": "red",
				"Not Started": "red",
				"In Process": "orange",
				"Completed": "green",
				"Cancelled": "gray"
			}[doc.status], "status,=," + doc.status];
		}
	}
};
