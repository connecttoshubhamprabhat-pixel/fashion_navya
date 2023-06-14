# Copyright (c) 2023, pawasthy11@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, time_diff_in_hours
from frappe import utils



def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data



def get_columns():
	return [
		{
			"label": _("Stock Entry"),
			"fieldtype": "Link",
			"fieldname": "se",
			"options": "Stock Entry",
			"width":200,
		},
		{
			"label": _("Stock Entry Type"),
			"fieldtype": "Link",
			"fieldname": "set",
			"options":"Stock Entry Type",
			"width":200,
		},
		{
			"label": _("Created By"),
			"fieldtype": "Data",
			"fieldname": "cb",
			"width":200,
		},
		{
			"label": _("Creation Date"),
			"fieldtype": "Date",
			"fieldname": "cd",
			"width":150,
		},
		{
			"label": _("Item Count"),
			"fieldtype": "Data",
			"fieldname": "ic",
			"width":90,
		},




		]



def get_data(filters):
	data = []
	if not filters :
		return []

	if filters.from_date > filters.to_date:
		frappe.msgprint(_("From Date can not be greater than To Date"))
		return data

	print(filters.from_date,'af')
	print(filters.to_date,'at')
	todays=utils.today()

	if filters.stype:
		se=frappe.db.sql(""" select name, posting_date,stock_entry_type from `tabStock Entry` where docstatus <2 and posting_date between '{}' and '{}' and stock_entry_type='{}' and CAST(modified AS date)='{}' and workflow_state in ('Authorised','Received')  """.format(filters.from_date,filters.to_date,filters.stype,todays),as_dict=1)
	else:
		se=frappe.db.sql(""" select name, posting_date,stock_entry_type from `tabStock Entry` where docstatus=0 and posting_date between '{}' and '{}'  and CAST(modified AS date)='{}' and workflow_state in ('Authorised','Received') """.format(filters.from_date,filters.to_date,todays),as_dict=1)

	for i in se:
		sedoc=frappe.get_doc("Stock Entry",i['name'])
		items=sedoc.items
		d={}
		d['se']=i['name']
		d['set']=sedoc.stock_entry_type
		d['cb']=sedoc.owner
		d['cd']=sedoc.posting_date
		d['ic']=len(items)
		data.append(d)







	return data
