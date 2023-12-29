// Copyright (c) 2023, pawasthy11@gmail.com and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Physical Stock Review"] = {
	"filters": [
		{
			fieldname: "phy",
			label:"Physical Stock Count",
			fieldtype: "Link",
			options: "Physical Stock Count",
			reqd: 1
		},
		{
			fieldname: "diff_type",
			label: __("Diff Qty Type"),
			fieldtype: "Select",
			options:["Plus","Minus","Both"],
			reqd:1
		},

	]
};
