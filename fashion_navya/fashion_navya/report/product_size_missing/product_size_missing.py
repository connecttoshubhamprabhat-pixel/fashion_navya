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
	conditions=[]
	# if not filters.item:
	# 	return []
	
	if not filters.get("project"):
		return []

	if filters.get("item"):
		item_data = filters.get("item")
		conditions.append(f"i.variant_of = '{item_data}'")

	if filters.get("warehouse"):
		warehouse_data = filters.get("warehouse")
		conditions.append(f"id.default_warehouse = '{warehouse_data}'")
	
	if filters.get("item_group"):
		item_group_data = filters.get("item_group")
		conditions.append(f"i.item_group = '{item_group_data}'")

	if filters.get("project"):
		project_data = filters.get("project")
		conditions.append(f"i.project = '{project_data}'")


	conditions_str = " AND ".join(conditions) if conditions else "1=1"
	items = frappe.db.sql(f"""select i.name 
					   from `tabItem` i 
					   JOIN `tabItem Default` id ON id.parent = i.name
					   JOIN `tabProject` p ON p.name = i.project
					   where i.has_variants != 1 and {conditions_str} """,as_dict = 1)

	
	if items:
		item_names = [item.get("name") for item in items]
		item_names_tuple = tuple(item_names)
		
		item_data = filters.get("item")
		if item_data:
			default_colors_query = frappe.db.sql(f"""
				SELECT pia.attribute_values 
				FROM `tabProject` p 
				JOIN `tabBOM Item` bi ON bi.parent = p.name
				JOIN `tabProject Item Attribute` pia ON pia.parent = p.name
				WHERE bi.item_code = '{item_data}' AND pia.attribute = 'Colour'
			""", as_dict=True)
		else:
			default_colors_query = frappe.db.sql(f"""
				SELECT pia.attribute_values 
				FROM `tabProject` p 
				JOIN `tabBOM Item` bi ON bi.parent = p.name
				JOIN `tabProject Item Attribute` pia ON pia.parent = p.name
				WHERE pia.attribute = 'Colour'
			""", as_dict=True)

		all_colors = list({color["attribute_values"] for color in default_colors_query if color.get("attribute_values")})
		
		for item in item_names:
			missing_size = get_missing_sizes(item)
			missing_color = get_missing_colors(item, all_colors)
			data.append({
				"item": item,
				"missing_size": missing_size,
				"missing_color": missing_color
			})

	return data

def get_missing_sizes(item):
	size_missing = []
	default_sizes = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]

	for size in default_sizes:
		split_sku = item.split("-")
		for i, part in enumerate(split_sku):
			if part in default_sizes:
				split_sku[i] = size
		join_final_name = "-".join(split_sku)

		if not frappe.db.exists("Item", join_final_name):
			size_missing.append(size)

	return ",".join(size_missing) if size_missing else "No"

def get_missing_colors(item, all_colors):
	color_missing = []
	all_colors = all_colors
	available_colors_query = frappe.db.sql(f"""
		SELECT iva.attribute_value
		FROM `tabItem` i 
		JOIN `tabItem Variant Attribute` iva ON iva.parent = i.name
		WHERE iva.attribute = 'Colour' AND i.name = '{item}'
	""", as_dict=True)

	colors = {color.get("attribute_value") for color in available_colors_query}
	available_colors = list(colors)
	separated_colors = all_colors[0].split(',')

	color_missing = [color for color in separated_colors if color not in available_colors]
	
	return ",".join(color_missing) if color_missing else "No"



def get_columns():
	return [
		{
			"label": "Item",
			"fieldtype": "Link",
			"fieldname": "item",
			"options": "Item",
			"width": 300,
		},
		{
			"label": "Missing Sizes",
			"fieldtype": "Data",
			"fieldname": "missing_size",
			"width": 300,
		},
		{
			"label": "Missing Color",
			"fieldtype": "Data",
			"fieldname": "missing_color",
			"width": 300,
		}
	]