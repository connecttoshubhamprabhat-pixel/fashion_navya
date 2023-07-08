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
			"label": _("Subcontracting Order"),
			"fieldtype": "Link",
			"fieldname": "subo",
			"options": "Subcontracting Order",
			"width":160,
		},
		{
			"label": _("Item"),
			"fieldtype": "Link",
			"fieldname": "item",
			"options":"Item",
			"width":100,
		},
		{
			"label": _("Item Name"),
			"fieldtype": "Data",
			"fieldname": "iname",
			"width":400,
		},
		{
			"label": _("Sub Orders Recepit"),
			"fieldtype": "Data",
			"fieldname": "subr",
			"width":160,
		},
		{
			"label": _("Stock Entry Manufacture"),
			"fieldtype": "Data",
			"fieldname": "sem",
			"width":188,
		},

	]


def get_data(filters):
	data = []

	ftr_str="  "
	if filters.suborder:
		ftr_str +=" and name='{}'  ".format(filters.suborder)
		
	get_sub=frappe.db.sql(""" select name from `tabSubcontracting Order` where docstatus=1  {} """.format(ftr_str),as_dict=1)
	if get_sub:
		for i in  get_sub:
			doc=frappe.get_doc("Subcontracting Order",i['name'])
			d={}
			d['subo']=i['name']
			for j in doc.items:
				itemdoc=frappe.get_doc("Item",j.item_code)
				if not filters.itemg:
					d['item']=itemdoc.name
					d['iname']=itemdoc.item_name
					getse=frappe.db.sql(""" select parent from `tabSubcontracting Receipt Item` where docstatus=1 and subcontracting_order='{}' """.format(doc.name),as_dict=1)
					if len(getse)!=0:
						d['subr']="Yes"
					else:
						d['subr']="No"
						
					getsem=frappe.db.sql(""" select parent from `tabStock Entry Detail` where docstatus=1 and subcontracted_item='{}'   and parent in (select name from `tabStock Entry` where docstatus=1  and subcontracting_order='{}') """.format(itemdoc.name,doc.name),as_dict=1)
					if len(getse)!=0:
						d['sem']="Yes"
						
					else:
						d['sem']="No"
					data.append(d)
					
					
				if filters.itemg:
					if itemdoc.item_group==filters.itemg:
						d['item']=itemdoc.name
						d['iname']=itemdoc.item_name
						getse=frappe.db.sql(""" select parent from `tabSubcontracting Receipt Item` where docstatus=1 and subcontracting_order='{}' """.format(doc.name),as_dict=1)
						if len(getse)!=0:
							d['subr']="Yes"
						else:
							d['subr']="No"
						

				
						getsem=frappe.db.sql(""" select parent from `tabStock Entry Detail` where docstatus=1 and subcontracted_item='{}'  and parent in (select name from `tabStock Entry` where docstatus=1  and subcontracting_order='{}') """.format(itemdoc.name,doc.name),as_dict=1)
						if len(getse)!=0:
							d['sem']="Yes"
							
						else:
							d['sem']="No"
						data.append(d)
	
	




	return data




