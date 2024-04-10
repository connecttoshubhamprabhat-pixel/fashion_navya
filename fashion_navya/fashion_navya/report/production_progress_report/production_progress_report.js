frappe.query_reports["Production Progress Report"] = {
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
					fieldname: "project",
					label: __("Project"),
					fieldtype: "Link",
					options: "Project",
					reqd: 0
				},



    ]
};
