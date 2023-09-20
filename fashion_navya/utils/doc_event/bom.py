import frappe
import json
from frappe.utils import cint, cstr, flt

@frappe.whitelist()
def customise_item_fetch_value(doc,method):
	if doc.get("__islocal"):
		return
	item=frappe.get_doc("Item",doc.item)
	if item.has_variants==0 and item.item_group=="Customise":
		if not doc.sales_order:
			frappe.throw("In Case,Sales Order is required")
