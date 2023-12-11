import frappe


@frappe.whitelist()
def bom_notify():
	get_mr=frappe.db.sql("""select name from `tabMaterial Request` where  material_request_type='Manufacture' and  docstatus<2 and custom_bom=0  """.format(),as_dict=1)
	if get_mr:
		for m in get_mr:
			doc=frappe.get_doc("Material Request",m['name'])
			if doc.custom_bom==0:
				doctype=doc.doctype
				des=" Measurement के हिसाब से BOM  को सेट करो ||,MR No:- {}".format(doc.name)
				user_list=['vivekd@navyacustom.com','gaurav@example.com']
				for i in user_list:
					d={'doctype':"ToDo","priority":"High","reference_type":doctype}
					d['description']=des
					d['reference_name']=doc.name
					d['assigned_by']="amita@navya.biz"
					d['allocated_to']=i
					td=frappe.get_doc(d)
					td.insert()
					frappe.db.commit()





@frappe.whitelist()
def wo_notify():
	get_mr=frappe.db.sql("""select name from `tabWork Order` where docstatus<2 and status='Not Started'  """.format(),as_dict=1)
	if get_mr:
		for m in get_mr:
			doc=frappe.get_doc("Work Order",m['name'])
			doctype=doc.doctype
			des=" Work Order is created||,Work order No:- {}".format(doc.name)
			user_list=['vivekd@navyacustom.com','gaurav@example.com']
			for i in user_list:
				d={'doctype':"ToDo","priority":"High","reference_type":doctype}
				d['description']=des
				d['reference_name']=doc.name
				d['assigned_by']="amita@navya.biz"
				d['allocated_to']=i
				td=frappe.get_doc(d)
				td.insert()
				frappe.db.commit()
