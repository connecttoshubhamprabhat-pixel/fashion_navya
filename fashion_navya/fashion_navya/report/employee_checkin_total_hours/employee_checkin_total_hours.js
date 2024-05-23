// Copyright (c) 2024, pawasthy11@gmail.com and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Checkin Total Hours"] = {
    "filters": [{
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
        {
            fieldname: "branch",
            label: __("Branch"),
            fieldtype: "Link",
            options: "Branch",
			default:"Sainik Farms"
        },


    ]
};