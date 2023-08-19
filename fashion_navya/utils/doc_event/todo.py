import frappe


@frappe.whitelist()
def create_todo(doc,method):
	doctype=doc.doctype
	user_list=['vivekd@navyacustom.com']
	for i in user_list:
		d={'doctype':"ToDo","priority":"High","reference_type":doctype}
		d['description']="Project is created"
		d['reference_name']=doc.name
		d['assigned_by']="amita@navya.biz"
		d['allocated_to']=i
		td=frappe.get_doc(d)
		td.insert()
