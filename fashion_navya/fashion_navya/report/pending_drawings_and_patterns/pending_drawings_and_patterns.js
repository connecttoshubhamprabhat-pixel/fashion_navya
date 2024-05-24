// Copyright (c) 2024, pawasthy11@gmail.com and contributors
// For license information, please see license.txt

frappe.query_reports["Pending Drawings and Patterns"] = {
	"filters": [
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			hidden:1,
			options: "Project"
		},
		{
			fieldname: "project_range",
			label: __("Project Range"),
			fieldtype: "Select",
			default:"1300-1500",
			options:["1400-1500","1500-1600","1600-1700","1700-1900"],
			reqd: 1
		},




	]
};
