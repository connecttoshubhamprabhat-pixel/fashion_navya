import frappe

@frappe.whitelist()
def remove_disabled(doc,method):
	if doc.mr_items:
		for i in doc.mr_items:
			item=frappe.get_doc("Item",i.item_code)
			if item.disabled==1:
				msg="Row {} item is disabled ,Please remove Disabled Item".format(i.idx)
				frappe.throw(msg)
