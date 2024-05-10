// Copyright (c) 2024, pawasthy11@gmail.com and contributors
// For license information, please see license.txt

frappe.query_reports["Product Size Missing"] = {
	"filters": [
		{
			fieldname: "item",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item",
			//reqd: 1
		},
		



	]
};
