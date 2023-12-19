import frappe


@frappe.whitelist()
def link_setup_subcontrcat(doc,method):
	if doc.items:
		po=doc.items[0].purchase_order
		get_orders=frappe.db.sql("""select name from `tabSubcontracting Order`  docstatus<2 and purchase_order='{}'   """.format(po),as_dict=1)
		if len(get_orders)!=0:
			frappe.db.sql("""update `tabSubcontracting Order` set custom_purchase_invoice='{}' where docstatus<2 and name='{}'  """.format(do.name,get_orders[0]['name']))
			frappe.db.commit()
