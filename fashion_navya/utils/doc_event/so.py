import frappe


@frappe.whitelist()
def check_sample_items(doc,method):
	for i in doc.items:
		item=frappe.get_doc("Item",i.item_code)
		if item.item_group=="Sample":
			frappe.throw("Sample product is not for sale")
