# Copyright (c) 2023, pawasthy11@gmail.com and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe import _
from frappe.utils import flt, time_diff_in_hours


def execute(filters):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_data(filters):
	data = []
	if not filters.phy:
		return []
	phy=frappe.db.sql("""select * from `tabPhysical Scan` where parent='{}' """.format(filters.phy),as_dict=1)
	#doc=frappe.get_doc("Physical Stock Review",filters.phy)
	if filters.diff_type=="Plus" and len(phy)!=0:
		if len(phy)!=0:
			for i in phy:
				#parent=frappe.db.sql("""select * from `tabPhysical Stock Review` where name='{}'  """.format(i['parent']),as_dict=1)
				if i['dqty']>0:
					d={}
					#d['warehouse']=i['warehouse']
					d['item']=i['item_code']
					d['wqty']=i['aqty']
					d['sqty']=i['sqty']
					d['dqty']=i['dqty']
					#d['date']=parent[0]['posting_date']
					data.append(d)

	if filters.diff_type=="Both" and len(phy)!=0:
		if phy:
			for i in phy:
				d={}
				#parent=frappe.db.sql("""select * from `tabPhysical Stock Review` where name='{}'  """.format(i['parent']),as_dict=1)
				#d['warehouse']=i['warehouse']
				d['item']=i['item_code']
				d['wqty']=i['aqty']
				d['sqty']=i['sqty']
				d['dqty']=i['dqty']
				#d['date']=parent[0]['posting_date']
				data.append(d)



	if filters.diff_type=="Minus" and len(phy)!=0:
		if phy:
			for i in phy:
				#parent=frappe.db.sql("""select * from `tabPhysical Stock Review` where name='{}'  """.format(i['parent']),as_dict=1)
				if i['dqty']<0:
					d={}
					#d['warehouse']=i['warehouse']
					d['item']=i['item_code']
					d['wqty']=i['aqty']
					d['sqty']=i['sqty']
					d['dqty']=i['dqty']
					#d['date']=parent[0]['posting_date']
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
		}]
