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
	if parent.item_group=="M kit" or  parent.has_variants==1 or doc.bom_creator:
		return

	if parent.item_group in ['Sample','Ready Stock']:
		for i in doc.items:
			if i.idx==1:
				doc_item=frappe.get_doc("Item",i.item_code)
				if doc_item.item_group!="M kit":
					frappe.throw("Frist Row Item is not Kit Item")



@frappe.whitelist()
def fetch_fabrice_ptt(doc,method):
	if doc.item:
		split=doc.item.split("-")
		get_name=split[:-1]
		join="-".join(get_name)
		if frappe.db.exists("Item",join):
			get__ppt=frappe.db.sql("""select name from `tabPattern` where item_code='{}' and docstatus=1 and  sheet_no=2 """.format(join),as_dict=1)
			if get__ppt:
				get_fabric=frappe.db.sql(""" select * from `tabChild Patterns` where parent='{}' """.format(get__ppt[0]['name']),as_dict=1)
				if len(get_fabric)!=0:
					if get_fabric[0]['fabric_1']:
						doc.set("custom_fabric_one",get_fabric[0]['fabric_1'])
				
					if get_fabric[0]['fabric_2']:
						doc.set("custom_fabric_two",get_fabric[0]['fabric_2'])


