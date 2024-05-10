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
	if not filters.item:
		return []
		
		
	item=filters.item
	missing_size=get_mising_sizes(item)
	d={'missing_size':missing_size,"item":item}
	data.append(d)
		

	
		
	
	return data





def get_mising_sizes(item):
	size_missing=[]
	default_sizes=["XS","S","M","L","XL","XXL","XXXL"]
	for j in default_sizes:
		split_sku=item.split("-")
		for i, n in enumerate(split_sku):
			if n in default_sizes:
				split_sku[i]=j
		join_final_name="-".join(split_sku)
		if not frappe.db.exists("Item",join_final_name):
			size_missing.append(j)

	print(size_missing,'size_missing')
	if size_missing:
		join_list=",".join(size_missing)
		return join_list
	else:
		return "No"

		





def get_columns():
	return [

		{
			"label":"Item",
			"fieldtype": "Link",
			"fieldname": "item",
			"options": "Item",
			"width":230,
		},
		{
			"label":"Missing Sizes",
			"fieldtype": "Data",
			"fieldname": "missing_size",
			"width":220,
		},
		


]
