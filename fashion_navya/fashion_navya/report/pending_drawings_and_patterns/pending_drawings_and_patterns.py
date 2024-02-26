# Copyright (c) 2023, pawasthy11@gmail.com and contributors
# For license information, please see license.txt
import frappe
from frappe import _
import re
from frappe.utils import flt, time_diff_in_hours



def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_data(filters):
	data = []
	condition=" "
	if not filters.project:
		return []
		
	get_items=frappe.db.sql("""select DISTINCT name from `tabItem`  where project='{}' and  variant_of is not null  """.format(filters.project),as_dict=1)
	get_mtm=frappe.db.sql("""select DISTINCT name from `tabItem`  where project='{}' and name like '%MTM%'  """.format(filters.project),as_dict=1)
	if get_items:
		for i in get_items:
			d={}
			item=i['name']
			d['item']=item
			doc=frappe.get_doc("Item",item)
			sil=" ".join(re.findall("[a-zA-Z]+",doc.variant_of))
			d['silvit']=sil
			d['item_name']=doc.item_name

			ptt=frappe.db.sql(""" select name from `tabPattern` where item_code='{}' and docstatus=1 and sheet_no in (2,4) """.format(item),as_dict=1)
			drw=frappe.db.sql(""" select name from `tabDrawing` where item_code='{}' and docstatus=1 """.format(item),as_dict=1)
			if len(ptt)>2:
				d['isptt']="Yes"
			else:
				d['isptt']="No"

			if len(drw)!=0:
				d['isdrw']="Yes"
			else:
				d['isdrw']="No"
				
			data.append(d)
	
	if get_mtm:
		#frappe.msgprint("feb22")
		for j in get_mtm:
			d={}
			item=j['name']
			d['item']=item
			doc=frappe.get_doc("Item",item)
			split=doc.name.split("-")
			#sil=" ".join(re.findall("[a-zA-Z]+",doc.variant_of))
			#d['silvit']=sil
			d['item_name']=doc.item_name

			ptt=frappe.db.sql(""" select name from `tabPattern` where item_code='{}' and docstatus=1 and sheet_no in (2,4) """.format(item),as_dict=1)
			drw=frappe.db.sql(""" select name from `tabDrawing` where item_code='{}' and docstatus=1 """.format(item),as_dict=1)
			if len(ptt)>2:
				d['isptt']="Yes"
			else:
				d['isptt']="No"

			if len(drw)!=0:
				d['isdrw']="Yes"
			else:
				d['isdrw']="No"
				
			data.append(d)
	
			

			
			
	
	return data








def get_columns():
	return [

		{
			"label":"Item",
			"fieldtype": "Link",
			"fieldname": "item",
			"options": "Item",
			"width":170,
		},
		{
			"label":"Item Name",
			"fieldtype": "Data",
			"fieldname": "item_name",
			"width":210,
		},
		{
			"label":"Silhouette",
			"fieldtype": "Data",
			"fieldname": "silvit",
			"width":180,
		},
	
		# {
		# 	"label": _("Pattern"),
		# 	"fieldtype": "Link",
		# 	"fieldname": "pattern",
		# 	"options": "Pattern",
		# 	"width":180,
		# },

		{
			"label":"IS Pattern?",
			"fieldtype": "Select",
			"fieldname": "isptt",
			"options":["","Yes","No"],
			"width":165,
		},

		# {
		# 	"label": _("Drawing"),
		# 	"fieldtype": "Link",
		# 	"fieldname": "drw",
		# 	"options": "Drawing",
		# 	"width":180,
		# },

		
		{
			"label":"IS Drawing?",
			"fieldtype": "Select",
			"fieldname": "isdrw",
			"options":["","Yes","No"],
			"width":165,
		},



]
