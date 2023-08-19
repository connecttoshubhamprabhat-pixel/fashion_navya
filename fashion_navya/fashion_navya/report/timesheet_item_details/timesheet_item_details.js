// Copyright (c) 2023, pawasthy11@gmail.com and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Timesheet Item Details"] = {
	
	"filters": [
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
			//reqd: 1
		},
		{
			fieldname: "item",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item",
			//reqd: 1
		},
		{
			fieldname: "item_type",
			label: __("Item Type"),
			fieldtype: "Select",
			options:["","variant","template","Enabled"]
			//reqd: 1
		},

		{
			fieldname: "range",
			label:"Date Range",
			fieldtype: "Select",
			options: ["Last Day","Today","Current Month","Last Months"],
			default:"Last Day"
			//reqd: 1
		},
		
	]
}

