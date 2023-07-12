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
		receive_to_customer=[]
		receive_to_bank=[]
		for i in get_all_pe:
			d={}
			docpe=frappe.get_doc("Payment Entry",i['name'])
			if docpe.payment_type=="Receive":
				if docpe.paid_amount:
					d['ctor']=docpe.paid_to
					d['ramt']=float(docpe.paid_amount)

			if docpe.payment_type=="Internal Transfer":
				if docpe.paid_amount:
					d['ctob']=docpe.paid_to
					d['bamt']=float(docpe.paid_amount)
			data.append(d)



	return data








def get_columns():
	return [

		{
			"label":"Cash To Customer",
			"fieldtype": "Link",
			"fieldname": "ctor",
			"options": "Account",
			"width":180,
		},
		{
			"label": _("Cash To Bank"),
			"fieldtype": "Link",
			"fieldname": "ctob",
			"options": "Account",
			"width":180,
		},

		{
			"label":"Customer received Amount",
			"fieldtype": "Data",
			"fieldname": "ramt",
			"width":180,
		},
		{
			"label":"Cash Deposited Bank Amount",
			"fieldtype": "Data",
			"fieldname": "bamt",
			"width":165,
		},



]
