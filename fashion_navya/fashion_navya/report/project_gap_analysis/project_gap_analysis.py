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

	doc=frappe.get_doc("Project",filters.project)
	get_templates=frappe.db.sql("""select name from `tabItem` where has_variants=1 and project='{}'  """.format(filters.project),as_dict=1)
	if len(get_templates)!=0:
		for i in get_templates:
			templates=i['name']
			count_temp=0
			split_templates=templates.split("-")
			silvit_name=split_templates[-1]
			get_items=frappe.db.sql("""select name from `tabItem` where variant_of='{}'  """.format(templates),as_dict=1)
			if len(get_items)==0:
				d={}
				d['silhoutte']=silvit_name
				d['template']=templates
				d['smplsizemiss']="ALL SMPL Size missing"
				d['rtwsizemiss']="ALl RTW Size missing"
				data.append(d)
				continue
			all_rtw_sizes=[]
			all_smpl_sizes=[]
			if len(get_items)!=0:
				for product in get_items:
					#print(silvit,'aa23')
					d={}
					if count_temp==0:
						d['silhoutte']=silvit_name
						d['template']=templates

					item=product['name']
					itemdoc=frappe.get_doc("Item",item)
					if itemdoc.item_group=="Ready Stock":
						for a in itemdoc.attributes:
							if a.attribute=="Size":
								all_rtw_sizes.append(a.attribute_value)
								break

					if itemdoc.item_group=="Sample":
						for a in itemdoc.attributes:
							if a.attribute=="Size":
								all_smpl_sizes.append(a.attribute_value)
								break

					netstock=[0]
					not_wo_qty=[0]
					in_wo_qty=[0]
					all_sheets=[1,2,3,4]
					approved_sheet=[]
					get_approved_ppt=frappe.db.sql("""select sheet_no from `tabPattern` where item_code='{}' and docstatus=1  """.format(item),as_dict=1)
					if len(get_approved_ppt)!=0:
						for ptt in get_approved_ppt:
							if ptt['sheet_no']!=None:
								approved_sheet.append(int(ptt['sheet_no']))

					dict_all_sheets=set(all_sheets)
					dict_all_approved_sheet=set(approved_sheet)
					final_miss_patt=list(dict_all_sheets-dict_all_approved_sheet)
					#string_pattern=",".join(final_miss_patt)

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
					count_temp+=1


				if frappe.db.exists("Silhouette",silvit_name):
					get_smpl_silvit_sizes=[]
					get_rtw_silvit_sizes=[]
					sildoc=frappe.get_doc("Silhouette",silvit_name)
					if sildoc.capacity__silhouette:
						for sil_smpl in sildoc.capacity__silhouette:
							get_smpl_silvit_sizes.append(sil_smpl.sizes)

					if sildoc.ready:
						for sil_rtw in sildoc.ready:
							get_rtw_silvit_sizes.append(sil_rtw.sizes)

					dict_get_smpl_silvit_sizes=set(get_smpl_silvit_sizes)
					dict_get_rtw_silvit_sizes=set(get_rtw_silvit_sizes)
					dict_all_rtw_sizes=set(all_rtw_sizes)
					dict_all_smpl_sizes=set(all_smpl_sizes)
					final_miss_smpl=list(dict_get_smpl_silvit_sizes-dict_all_smpl_sizes)
					final_miss_rtw=list(dict_get_rtw_silvit_sizes-dict_all_rtw_sizes)
					final_miss_smpl_str=",".join(final_miss_smpl)
					final_miss_rtw_str=",".join(final_miss_rtw)
					d_1={}
					d_1['smplsizemiss']=final_miss_smpl_str
					d_1['rtwsizemiss']=final_miss_rtw_str
					d_1['silhoutte']=silvit_name
					d_1['template']=templates
					data.append(d_1)















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
			"label":"RTW/SizeMissing",
			"fieldtype": "data",
			"fieldname": "rtwsizemiss",
			"width":500,
		},
		{
			"label":"SMPL/SizeMissing",
			"fieldtype": "data",
			"fieldname": "smplsizemiss",
			"width":500,
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
			"label":"Pattern/pending/PRSMPL",
			"fieldtype": "data",
			"fieldname": "prsheet",
			"width":150,
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
			"label":"Pattern/Pending/SMPL",
			"fieldtype": "data",
			"fieldname": "smplsheet",
			"width":150,
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
			"label":"Pattern/Pending/RTW",
			"fieldtype": "data",
			"fieldname": "rtwsheet",
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
