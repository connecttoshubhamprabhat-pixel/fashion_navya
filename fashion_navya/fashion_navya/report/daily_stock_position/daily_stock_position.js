// Copyright (c) 2024, pawasthy11@gmail.com and contributors
// For license information, please see license.txt

frappe.query_reports["Daily Stock Position"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"hidden":0,
			"default": frappe.datetime.get_today()
	},
	{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"hidden":0,
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
{
	"fieldname": "day_type",
	"label": __("Day Type"),
	"fieldtype": "Select",
	"default":"Today",
	"options":["Today","Yesterday","No Time"],
},

	]
};
