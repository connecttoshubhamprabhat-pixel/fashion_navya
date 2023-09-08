import frappe


@frappe.whitelist()
def fetch_work_order(doc,method):
	for i in doc.items:
		wk=frappe.db.sql("""select name from `tabWork Order` where docstatus < 2 and bom_no='{}'    """.format(i.bom),as_dict=1)
		if len(wk)!=0:
			doc.set("work_order",wk[0]['name'])
