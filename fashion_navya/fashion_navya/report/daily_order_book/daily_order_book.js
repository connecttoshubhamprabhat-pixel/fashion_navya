// Copyright (c) 2024, pawasthy11@gmail.com and contributors
// For license information, please see license.txt

frappe.query_reports["Daily Order Book"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"hidden":1,
			"default": frappe.datetime.get_today()
	},
	{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"hidden":1,
			"default": frappe.datetime.get_today()
	},
	{
		"fieldname": "shop",
		"label": __("Shop"),
		"fieldtype": "Select",
		"default":"",
		"hidden":1,
		"options":["","Santushti - NAVYA","Pune - NAVYA"],
},

	]
};
