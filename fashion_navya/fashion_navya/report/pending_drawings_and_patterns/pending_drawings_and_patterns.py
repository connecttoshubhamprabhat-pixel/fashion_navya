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
	condition = ""

	if filters.project_range == "1400-1500":
		condition = "  CAST(SUBSTRING(`project`, 6) AS UNSIGNED) BETWEEN 1400 AND 1500"
	elif filters.project_range == "1500-1600":
		condition = "   CAST(SUBSTRING(`project`, 6) AS UNSIGNED) BETWEEN 1500 AND 1600"
	elif filters.project_range == "1600-1700":
		condition = "  CAST(SUBSTRING(`project`, 6) AS UNSIGNED) BETWEEN 1600 AND 1700"
	elif filters.project_range == "1800-1900":
		condition = "  CAST(SUBSTRING(`project`, 6) AS UNSIGNED) BETWEEN 1800 AND 1900"

	if condition:
		get_items = frappe.db.sql("""
            SELECT DISTINCT name
            FROM `tabItem`
            WHERE item_group IN ('Customise', 'Ready Stock', 'Sample', 'Template')
            AND {}
        """.format(condition), as_dict=1)

		for i in get_items:
			d = {}
			item = i['name']
			d['item'] = item
			doc = frappe.get_doc("Item", item)
			print(doc.name)
			if doc.variant_of:
				sil = " ".join(re.findall("[a-zA-Z]+", doc.variant_of))
				d['silvit'] = sil

			d['item_name'] = doc.item_name

			ptt = frappe.db.sql("""
                SELECT name
                FROM `tabPattern`
                WHERE item_code = %s AND docstatus = 1 AND sheet_no IN (2, 4)
            """, item, as_dict=1)


			drw = frappe.db.sql("""
                SELECT name
                FROM `tabDrawing`
                WHERE item_code = %s AND docstatus = 1
            """, item, as_dict=1)

			d['isptt'] = "Yes" if len(ptt) >= 2 else "No"
			d['isdrw'] = "Yes" if len(drw) != 0 else "No"

			# Only add items missing drawing or pattern
			if d['isptt'] == "No" or d['isdrw'] == "No":
				data.append(d)

	return data

def get_columns():
    return [
        {
            "label": "Item",
            "fieldtype": "Link",
            "fieldname": "item",
            "options": "Item",
            "width": 170,
        },
        {
            "label": "Item Name",
            "fieldtype": "Data",
            "fieldname": "item_name",
            "width": 210,
        },
        {
            "label": "Silhouette",
            "fieldtype": "Data",
            "fieldname": "silvit",
            "width": 180,
        },
        {
            "label": "IS Pattern?",
            "fieldtype": "Select",
            "fieldname": "isptt",
            "options": ["", "Yes", "No"],
            "width": 165,
        },
        {
            "label": "IS Drawing?",
            "fieldtype": "Select",
            "fieldname": "isdrw",
            "options": ["", "Yes", "No"],
            "width": 165,
        },
    ]
