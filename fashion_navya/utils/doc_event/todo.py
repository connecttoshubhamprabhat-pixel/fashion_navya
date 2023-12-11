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



@frappe.whitelist()
def create_todo_cs(doctype=None,name=None,msg=None,action=None,user_list=None,docstatus=0):
	if not doctype and not name and not user_list:
		return

	user_lists=json.loads(user_list)
	#user_lists=["pawasthy11@gmail.com"]
	if user_lists:
		for i in user_lists:
			d={'doctype':"ToDo","priority":"High","reference_type":doctype}
			d['description']=msg
			d['reference_name']=name
			d['assigned_by']="amita@navya.biz"
			d['allocated_to']=i
			td=frappe.get_doc(d)
			td.insert()
			frappe.db.commit()







@frappe.whitelist()
def create_todo_mr_bom(doc,method):
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



@frappe.whitelist()
def create_todo_project(items=None,values=None):
	items=json.loads(items)
	values=json.loads(values)
	date=values.get("date")
	users=values.get("assign_to")
	des=values.get("description")
	if users:
		for i in users:
			#print(i,'iuuuuuuu')
			user=i
			for item in items:
				#print(item,'s')
				d={'doctype':"ToDo","priority":"High","reference_type":"Item"}
				d['description']=des
				d['reference_name']=item
				d['assigned_by']="amita@navya.biz"
				d['allocated_to']=user
				td=frappe.get_doc(d)
				td.insert()
				frappe.msgprint("Created")
