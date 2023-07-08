// Copyright (c) 2023, pawasthy11@gmail.com and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Report Subcontract Items List"] = {
	"filters": [

		{
			"label":"Subcontracting Order",
			"fieldtype": "Link",
			"fieldname": "suborder",
			"options":"Subcontracting Order"
		},
		{
			"label":"Item Group",
			"fieldtype": "Link",
			"fieldname": "itemg",
			"options":"Item Group"
		},

	]
};
