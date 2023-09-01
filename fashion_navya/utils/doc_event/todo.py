import frappe
import json


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


@frappe.whitelist()
def create_todo_automated(doctype=None,name=None,users=None):
	if not name:
		return

	if not users:
		users=['amita@navya.biz',"neha@navyacustom.com"]
		d={'doctype':"ToDo","priority":"High","reference_type":doctype}
		msg="Automated Internal Transfer Entry"
		d['description']=msg
		d['reference_name']=name
		d['assigned_by']="amita@navya.biz"
		for i in users:
			d['allocated_to']=i
			try:
				td=frappe.get_doc(d)
				td.insert()
				frappe.db.commit()
			except:
				continue
	if not users:
		users=['amita@navya.biz',"neha@navyacustom.com"]
		d={'doctype':"ToDo","priority":"High","reference_type":doctype}
		msg="Automated Internal Transfer Entry"
		d['description']=msg
		d['reference_name']=name
		d['assigned_by']="amita@navya.biz"
		for i in users:
			d['allocated_to']=i
			try:
				td=frappe.get_doc(d)
				td.insert()
				frappe.db.commit()
			except:
				continue
	if not users:
		users=['amita@navya.biz',"neha@navyacustom.com"]
		d={'doctype':"ToDo","priority":"High","reference_type":doctype}
		msg="Automated Internal Transfer Entry"
		d['description']=msg
		d['reference_name']=name
		d['assigned_by']="amita@navya.biz"
		for i in users:
			d['allocated_to']=i
			try:
				td=frappe.get_doc(d)
				td.insert()
				frappe.db.commit()
			except:
				continue
