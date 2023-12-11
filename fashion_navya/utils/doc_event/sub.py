import frappe


@frappe.whitelist()
def fetch_work_order(doc,method):
	for i in doc.items:
		wk=frappe.db.sql("""select name from `tabWork Order` where docstatus < 2 and bom_no='{}'    """.format(i.bom),as_dict=1)
		if len(wk)!=0:
			doc.set("work_order",wk[0]['name'])


#rate change after submit
@frappe.whitelist()
def update_rate_after_submit(doc,method):
	if doc.docstatus==3 and doc.status in ['Partially Received','Partial Material Transferred',"Open","Material Transferred"]:
		po=frappe.get_doc("Purchase Order",doc.purchase_order)
		if po.docstatus==1:
			for i in po.items:
				frappe.db.sql("""update `tabSubcontracting Order Item` set rate='{}' where parent='{}' and item_code='{}'  """.format(i.rate,doc.name,i.fg_item))
				frappe.db.commit()

