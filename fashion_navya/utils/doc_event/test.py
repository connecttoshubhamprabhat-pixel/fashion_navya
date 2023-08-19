import frappe

#barcode
@frappe.whitelist()
def set_barcode_all(group=None):
	items=frappe.db.sql(""" select name from `tabItem` where item_group='{}' and ignore_project=0 and item_bcode_no is null  """.format(group),as_dict=1)
	for i in items:
		print(i['name'])
		doc=frappe.get_doc("Item",i['name'])
		
		try:
			doc.set("ignore_project",1)
			doc.save()
			frappe.db.commit()
		except:
			pass
