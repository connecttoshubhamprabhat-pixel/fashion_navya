// Copyright (c) 2024, pawasthy11@gmail.com and contributors
// For license information, please see license.txt

frappe.query_reports["Product Size Missing"] = {
	"filters": [
		{
			fieldname: "item",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item",
			get_query: () => {
				return {
					filters: {
						"has_variants": 1
					}
				};
			}
		},
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			options: "Warehouse"
		},
		{
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "Link",
			options: "Item Group"
		},
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project"
		}
	]
};