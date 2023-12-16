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





@frappe.whitelist()
def remove_disabled_items(doc,method):
	if doc.items:
		for i in doc.items:
			item=frappe.get_doc("Item",i.item_code)
			if item.disabled==1:
				new_name=i.item_code+"-"+"New"
				if frappe.db.exists("Item",new_name):
					i.set("item_code",new_name)



@frappe.whitelist()
def before_submit_check_kit(doc,method):
	parent=frappe.get_doc("Item",doc.item)
	if parent.item_group=="M kit" or  parent.has_variants==1:
		return

	if parent.item_group in ['Sample','Ready Stock']:
		for i in doc.items:
			if i.idx==1:
				doc_item=frappe.get_doc("Item",i.item_code)
				if doc_item.item_group!="M kit":
					frappe.throw("Frist Row Item is not Kit Item")
