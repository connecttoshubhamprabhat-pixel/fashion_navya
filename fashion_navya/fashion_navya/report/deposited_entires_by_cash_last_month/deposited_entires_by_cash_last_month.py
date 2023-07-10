# Copyright (c) 2023, pawasthy11@gmail.com and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from frappe.utils import flt, time_diff_in_hours



def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_data(filters):
	data = []
	condition=" "
	if filters.from_date > filters.to_date:
		frappe.msgprint(_("From Date can not be greater than To Date"))
		return data
	condition +=" and posting_date between '{}' and '{}' and mode_of_payment='{}' ".format(filters.from_date,filters.to_date,filters.mop)
	get_all_pe=frappe.db.sql(""" select name from `tabPayment Entry` where docstatus=1  {} """.format(condition),as_dict=1)
	if len(get_all_pe)!=0:
		for i in get_all_pe:
			d={}
			docpe=frappe.get_doc("Payment Entry",i['name'])
			d['pe']=docpe.name
			d['af']=docpe.paid_from
			d['ato']=docpe.paid_to
			d['pa']=docpe.paid_amount
			d['ra']=docpe.received_amount
			data.append(d)


	return data








def get_columns():
	return [
		{
			"label": _("Payment Entry"),
			"fieldtype": "Link",
			"fieldname": "pe",
			"options": "Payment Entry",
			"width": 300,
		},

		{
			"label": _("Account From"),
			"fieldtype": "Link",
			"fieldname": "af",
			"options": "Account",
			"width": 200,
		},
		{
			"label": _("Account To"),
			"fieldtype": "Link",
			"fieldname": "ato",
			"options": "Account",
			"width":150,
		},

		{"label": _("Paid Amount"), "fieldtype": "Float", "fieldname": "pa", "width": 150},
		{"label": _("Received Amount"), "fieldtype": "Float", "fieldname": "ra", "width": 150},

]
