import frappe


@frappe.whitelist()
def check_sample_items(doc,method):
	for i in doc.items:
		item=frappe.get_doc("Item",i.item_code)
		if item.item_group=="Sample":
			frappe.throw("Sample product is not for sale")



@frappe.whitelist()
def get_items(name=None):
	if not name:
		return

	doc=frappe.get_doc("Estimate Sheet",name)
	items=[]
	if doc.so_items:
		for i in doc.so_items:
			d={}
			item=frappe.get_doc("Item",i.item_code)
			d['item_code']=i.item_code
			d['item_name']=item.item_name
			d['qty']=1
			items.append(d)
	if items:
		return items
