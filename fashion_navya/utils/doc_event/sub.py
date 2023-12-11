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
	if doc.docstatus==1:
		get_sub_order=frappe.db.sql("""select name from `tabSubcontracting Order` where docstatus=1 and purchase_order='{}' """.format(doc.name),as_dict=1)
		if get_sub_order:
			so=get_sub_order[0]['name']
			for i in doc.items:
				frappe.db.sql("""update `tabSubcontracting Order Item` set service_cost_per_qty={} where parent='{}' and item_code='{}'  """.format(i.rate,so,i.fg_item))
				frappe.db.commit()
