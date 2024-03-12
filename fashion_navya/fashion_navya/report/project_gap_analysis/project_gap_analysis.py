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
	condition=""
	record_filters = [
        ["project", "=", filters.project],
		["has_variants", "=",1],
    ]


	if not filters.project:
		return []

	items = frappe.get_all(
		"Item", filters=record_filters, fields=["name","variant_of","has_variants"]
    )

	doc=frappe.get_doc("Project",filters.project)
	if doc.project_silhoutte:
		for i in doc.project_silhoutte:
			silvit=i.silhoutte
			d={}
			d['silhoutte']=silvit
			get_templates=frappe.db.sql("""select item_code from `tabBOM Item` where parentfield="project_item" and parenttype="Project" and parent='{}' and item_code like '%-{}%'  """.format(doc.name,silvit),as_dict=1)
			if len(get_templates)!=0:
				d['template']=get_templates[0]['item_code']
				get_items=frappe.db.sql("""select DISTINCT name from `tabItem` where variant_of='{}'  """.format(get_templates[0]['item_code']),as_dict=1)
				if len(get_items)!=0:
					for product in get_items:
						item=product['name']
						netstock=[0]
						not_wo_qty=[0]
						in_wo_qty=[0]
						not_start=frappe.db.sql("""select sum(qty) as qty from `tabWork Order` where status='Not Started' and production_item='{}'  """.format(item),as_dict=1)
						inprocess=frappe.db.sql("""select sum(qty) as qty from `tabWork Order` where status='In Process' and production_item='{}'  """.format(item),as_dict=1)
						if len(not_start)!=0:
							if not_start[0]['qty']!=None:
								not_wo_qty.append(not_start[0]['qty'])

						if len(inprocess)!=0:
							if inprocess[0]['qty']!=None:
								in_wo_qty.append(inprocess[0]['qty'])



						get_bins=frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where actual_qty>0 and item_code='{}' """.format(item),as_dict=1)
						if len(get_bins)!=0:
							if get_bins[0]['qty']!=None:
								netstock.append(get_bins[0]['qty'])
						split_prodiuct=item.split("-")
						if "PRSMPL" in split_prodiuct:
							d['prsmpl']=item
							d['nsprsmpl']=sum(netstock)
							d['prwonot']=sum(not_wo_qty)
							d['prwoin']=sum(in_wo_qty)
						if "SMPL" in split_prodiuct:
							d['smpl']=item
							d['nssmpl']=sum(netstock)
							d['smplwonot']=sum(not_wo_qty)
							d['smplwoin']=sum(in_wo_qty)
						if "RTW" in split_prodiuct:
							d['rtw']=item
							d['nsrtw']=sum(netstock)
							d['rtwwonot']=sum(not_wo_qty)
							d['rtwwoin']=sum(in_wo_qty)

			data.append(d)





	return data








def get_columns():
	return [

		{
			"label":"Silhoutte",
			"fieldtype": "Link",
			"fieldname": "silhoutte",
			"options": "Project Silhoutte",
			"width":170,
		},
		{
			"label":"Template",
			"fieldtype": "Link",
			"fieldname": "template",
			"options": "Item",
			"width":300,
		},

		{
			"label":"PRSMPL",
			"fieldtype": "Link",
			"fieldname": "prsmpl",
			"options": "Item",
			"width":300,
		},
		{
			"label":"PRSMPL NET Stock",
			"fieldtype": "float",
			"fieldname": "nsprsmpl",
			"width":110,
		},
		{
			"label":"PRSMPL/wo/InProcess",
			"fieldtype": "float",
			"fieldname": "prwoin",
			"width":200,
		},
		{
			"label":"PRSMPL/wo/NotStart",
			"fieldtype": "float",
			"fieldname": "prwonot",
			"width":200,
		},
		{
			"label":"SMPL",
			"fieldtype": "Link",
			"fieldname": "smpl",
			"options": "Item",
			"width":300,
		},
		{
			"label":"SMPL NET Stock",
			"fieldtype": "float",
			"fieldname": "nssmpl",
			"width":110,
		},
		{
			"label":"SMPL/wo/Inprocess",
			"fieldtype": "float",
			"fieldname": "smplwoin",
			"width":200,
		},
		{
			"label":"SMPL/wo/NOTStart",
			"fieldtype": "float",
			"fieldname": "smplwonot",
			"width":200,
		},
		{
			"label":"RTW",
			"fieldtype": "Link",
			"fieldname": "rtw",
			"options": "Item",
			"width":300,
		},
		{
			"label":"RTW NET Stock",
			"fieldtype": "float",
			"fieldname": "nsrtw",
			"width":110,
		},
		{
			"label":"RTW/wo/InProcess",
			"fieldtype": "float",
			"fieldname": "rtwwoin",
			"width":200,
		},
		{
			"label":"RTW/wo/NOTStart",
			"fieldtype": "float",
			"fieldname": "rtwwonot",
			"width":200,
		},
		{
			"label":"Item Name",
			"fieldtype": "Data",
			"fieldname": "item_name",
			"width":210,
			"hidden":1
		},


]
