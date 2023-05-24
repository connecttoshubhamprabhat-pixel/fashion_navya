frappe.listview_settings['Work Order'] = {
	add_fields: ["bom_no", "status", "sales_order", "qty",
		"produced_qty", "expected_delivery_date", "planned_start_date", "planned_end_date"],
	filters: [["status", "!=", "Stopped"]],
	onload: function(listview) {
		let user=frappe.session.user
		console.log(user,'hello')
               if (user in ['neha@navyacustom.com',"pawasthy11@gmail.com","sosowon@navyacustom.com","ksvwon@navyacustom.com"]){
                    frappe.set_route("List", "Work Order", "Calendar");
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

