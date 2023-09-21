// Copyright (c) 2023, pawasthy11@gmail.com and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Amount received by Entries"] = {
	"filters": [
		{
				"fieldname": "from_date",
				"label": __("From Date"),
				"fieldtype": "Date",
				"default": frappe.datetime.get_today()
		},
		{
				"fieldname": "to_date",
				"label": __("To Date"),
				"fieldtype": "Date",
				"default": frappe.datetime.get_today()
		},



	]
};
