import frappe



@frappe.whitelist()
def customer_no_check_exists(doc,method):
	if doc.cnumber:
		no_exists=frappe.db.sql(""" select name from `tabCustomer` where cnumber='{}' and name!='{}'  """.format(doc.cnumber,doc.name),as_dict=1)
		if len(no_exists)!=0:
			frappe.throw("Number Already Exists")
