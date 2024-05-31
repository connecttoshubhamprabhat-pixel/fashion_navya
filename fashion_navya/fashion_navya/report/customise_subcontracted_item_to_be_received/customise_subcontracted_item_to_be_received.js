// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customise Subcontracted Item To Be Received"] = {
	"filters": [
		{
			label: __("Order Type"),
			fieldname: "order_type",
			fieldtype: "Select",
			options: ["Subcontracting Order"],
			default: "Subcontracting Order",
			hidden:1
		},

		{
			label: __("Item Group"),
			fieldname: "item_group",
			fieldtype: "Select",
			options: ["","Ready Stock","Sample","M kit","DPK","BPK","HEK"]
		},
		{
			label: __("Status"),
			fieldname: "status",
			fieldtype: "Select",
			options: ["","Completed","Not Started","In Process"]
		},
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project"
		},
		{
			fieldname: "supplier",
			label: __("Supplier"),
			fieldtype: "Link",
			options: "Supplier"
		},
		{
			fieldname:"from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			reqd: 1
		},
		{
			fieldname:"to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1
		},
	]
};
