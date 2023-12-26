# Copyright (c) 2023, pawasthy11@gmail.com and contributors
# For license information, please see license.txt

# import frappe
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
	if not filters.phy:
		return []
	doc=frappe.get_doc("Physical Stock Review",filters.phy)
	if filters.diff_type=="Plus" and doc.docstatus==1:
		if doc.items:
			for i in doc.items:
				if i.dqty>0:
					d={}
					d['warehouse']=doc.warehouse
					d['item']=i.item_code
					d['wqty']=i.aqty
					d['sqty']=i.sqty
					d['dqty']=i.dqty
					d['date']=i.posting_date
					data.append(d)

	if filters.diff_type=="Both" and doc.docstatus==1:
		if doc.items:
			for i in doc.items:
				d={}
				d['warehouse']=doc.warehouse
				d['item']=i.item_code
				d['wqty']=i.aqty
				d['sqty']=i.sqty
				d['dqty']=i.dqty
				d['date']=i.posting_date
				data.append(d)



	if filters.diff_type=="Minus" and doc.docstatus==1:
		if doc.items:
			for i in doc.items:
				if i.dqty<0:
					d={}
					d['warehouse']=doc.warehouse
					d['item']=i.item_code
					d['wqty']=i.aqty
					d['sqty']=i.sqty
					d['dqty']=i.dqty
					d['date']=i.posting_date
					data.append(d)

	return data



def get_columns():
	return [
		{
			"label": _("Date"),
			"fieldtype": "Data",
			"fieldname": "date",
			"width": 200,
		},
		{
			"label":"Warehouse",
			"fieldtype":"Link",
			"fieldname":"warehouse",
			"options":"Warehouse",
			"width":200,
		},

		{
			"label": _("Item"),
			"fieldtype": "Link",
			"fieldname": "item",
			"options": "Item",
			"width":200,
		},

		{
			"label": _("Scan Qty"),
			"fieldtype": "int",
			"fieldname": "sqty",
			"width": 200,
		},
		{
			"label": _("Warehouse Qty"),
			"fieldtype": "int",
			"fieldname": "wqty",
			"width": 200,
		},

		{
			"label": _("Diff Qty"),
			"fieldtype": "int",
			"fieldname": "dqty",
			"width": 200,
		},]
