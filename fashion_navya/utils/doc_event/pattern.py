import frappe
import re

@frappe.whitelist()
def create_version_ppt(name=None):
	if not name:
		return


@frappe.whitelist()
def fetch_silvit(doc,method):
	if doc.item_code:
		item=frappe.get_doc("Item",doc.item_code)
		if item.variant_of:
			e=re.findall(r'\d+',item.variant_of)
			m=[]
			for i in e:
				m.append(int(i))
			get_no=min(m)
			get_slit=frappe.db.sql("""select name from `tabSilhouette` where silhouette_no='{}'  """.format(str(get_no)),as_dict=1)
			if get_slit:
				doc.set("svitname",get_slit[0]['name'])



@frappe.whitelist()
def pattern_validation(doc,method):
	if doc.sheet_no==1 and doc.custom_automated==0:
		if not doc.drawing:
			frappe.throw("Drawing is missing")
		if doc.drawing:
			dr=frappe.get_doc("Drawing",doc.drawing)
			if dr.docstatus==0:
				frappe.throw("Drawing is not approved")
				
			if dr.item_code!=doc.item_code:
				frappe.throw("Drawing is not correct")

				
	

			
@frappe.whitelist()
def pattern_not_dup(doc,method):
	get_sheet=frappe.db.sql(""" select name from `tabPattern` where sheet_no='{}' and docstatus<2 and item_code='{}' and name!='{}'  """.format(doc.sheet_no,doc.item_code,doc.name),as_dict=1)
	if len(get_sheet)!=0 and doc.custom_automated==0:
		frappe.throw("Sheet No {} Exists".format(doc.sheet_no))


@frappe.whitelist()
def check_sheet_apprved(doc,method):
	sheet_no=[1,2,3,4,5]
	sheet=doc.sheet_no-1
	get_range=sheet_no[:sheet]
	if get_range and doc.custom_automated==0:
		for i in get_range:
			get_pp=frappe.db.sql("""select name from `tabPattern` where item_code='{}' and sheet_no='{}' and docstatus=0  """.format(doc.item_code,i),as_dict=1)
			if len(get_pp)!=0:
				msg="First Approve this sheet {}".format(i)
				frappe.throw(msg)



