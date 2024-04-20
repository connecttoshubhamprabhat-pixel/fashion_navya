import frappe
import json


@frappe.whitelist()
def create_todo(doc,method):
	doctype=doc.doctype
	user_list=['vivekd@navyacustom.com']
	drawing_user=["sweetyd@navyacustom.com"]
	for i in user_list:
		d={'doctype':"ToDo","priority":"High","reference_type":doctype}
		d['description']="Project is created"
		d['reference_name']=doc.name
		d['assigned_by']="amita@navya.biz"
		d['allocated_to']=i
		td=frappe.get_doc(d)
		td.insert()

	for i in drawing_user:
		d={'doctype':"ToDo","priority":"High","reference_type":doctype}
		d['description']="Please Start Work on Drawing"
		d['reference_name']=doc.name
		d['assigned_by']="amita@navya.biz"
		d['allocated_to']=i
		td=frappe.get_doc(d)
		exists=frappe.db.sql("""select name from `tabToDo` where reference_type='{}'  and reference_name='{}' and status!="Cancelled" """.format(doctype,doc.name),as_dict=1)
		if len(exists)==0:
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
			exists=frappe.db.sql("""select name from `tabToDo` where reference_type='{}'  and reference_name='{}' and status!="Cancelled" """.format(doctype,name),as_dict=1)
			if len(exists)==0:
				td.insert()
				frappe.db.commit()







@frappe.whitelist()
def create_todo_mr_bom(doc,method):
	if doc.custom_bom==0:
		doctype=doc.doctype
		des="BOM  is missing for MR items ||,MR No:- {}".format(doc.name)
		user_list=['veer@example.com']
		for i in user_list:
			d={'doctype':"ToDo","priority":"High","reference_type":doctype}
			d['description']=des
			d['reference_name']=doc.name
			d['assigned_by']="amita@navya.biz"
			d['allocated_to']=i
			td=frappe.get_doc(d)
			exists=frappe.db.sql("""select name from `tabToDo` where reference_type='{}'  and reference_name='{}' and status!="Cancelled" """.format(doctype,doc.name),as_dict=1)
			if len(exists)==0:
				td.insert()

	#bom notification
	for i in doc.items:
		if i.sales_order:
			bom_users=["vivekd@navyacustom.com","gaurav@example.com"]
			get_bom=frappe.db.sql("""select distinct name from `tabBOM` where item='{}' and docstatus=0  """.format(i.item_code),as_dict=1)
			if get_bom:
				for b in get_bom:
					for u in bom_users:
						d={'doctype':"ToDo","priority":"High","reference_type":"BOM"}
						d['description']="Please Approved BOM"
						d['reference_name']=b['name']
						d['assigned_by']="amita@navya.biz"
						d['allocated_to']=u
						td=frappe.get_doc(d)
						exists=frappe.db.sql("""select name from `tabToDo` where reference_type='{}'  and reference_name='{}' and status!="Cancelled" """.format("BOM",b['name']),as_dict=1)
						if len(exists)==0:
							td.insert()

			else:
				for ur in bom_users:
					d={'doctype':"ToDo","priority":"High","reference_type":"Item"}
					d['description']="Please Make BOM for Item"
					d['reference_name']=i.item_code
					d['assigned_by']="amita@navya.biz"
					d['allocated_to']=ur
					td=frappe.get_doc(d)
					exists=frappe.db.sql("""select name from `tabToDo` where reference_type='{}'  and reference_name='{}' and status!="Cancelled" """.format("Item",i.item_code),as_dict=1)
					if len(exists)==0:
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



@frappe.whitelist()
def create_todo_urgent(emp=None,task=None,doctype=None):
	user_list=[]
	get_id=frappe.db.sql("""select user_id from `tabEmployee` where name='{}' """.format(emp),as_dict=1)
	if get_id:
		user_list.append(get_id[0]['user_id'])
		
	for i in user_list:
		d={'doctype':"ToDo","priority":"High","reference_type":doctype}
		d['description']="यह कार्य आज अत्यावश्यक है(This task is essential today)"
		d['reference_name']=task
		d['assigned_by']="amita@navya.biz"
		d['allocated_to']=i
		td=frappe.get_doc(d)
		td.insert()
		frappe.msgprint("TODO is created")






##################################################################################

# Define a function to be executed on submission of the document
def create_todo_on_send_to_approve_pattern_doc(doc, method):
	try:
		# Check if the document is being submitted
		if doc.workflow_state == "Authorisation Pending":
			# Create a new ToDo document
			todo = frappe.new_doc("ToDo")
			# Set the fields as per your requirements
			todo.status = "Open"
			todo.priority = "High"
			todo.todo_title = None
			todo.color = None
			todo.date = frappe.utils.today()
			todo.allocated_to = "amita@navya.biz"
			todo.allot_to_user =  "amita@navya.biz"
			todo.full_name = "Amita Adlakha"
			todo.description = "Mam, Please approve this pattern."
			todo.reference_type = "Pattern"
			todo.reference_name = doc.name
			todo.project = None
			todo.role = None
			todo.assigned_by = doc.modified_by
			todo.assigned_by_full_name = frappe.get_value("User", doc.modified_by, "full_name")
			print("##################################################################################################")
			# Save and submit the ToDo document
			todo.insert(ignore_permissions=True)
			# todo.submit()
			frappe.db.commit()
			frappe.msgprint("ToDo created and submitted successfully.")


	except Exception as e:
		frappe.log_error(f"Error creating and submitting ToDo: {e}")
######################################################################################




# Define a function to be executed on submission of the document
def create_todo_on_submit_drawing_doc(doc, method):
	try:
		# Check if the document is being submitted
		if doc.docstatus == 1:
			# Create a new ToDo document
			todo = frappe.new_doc("ToDo")
			# Set the fields as per your requirements
			todo.status = "Open"
			todo.priority = "High"
			todo.todo_title = None
			todo.color = None
			todo.date = frappe.utils.today()
			todo.allocated_to = "gaurav@example.com"
			todo.allot_to_user = "gaurav@example.com"
			todo.full_name = "Gaurav Basoya"
			todo.description = "Hey, This Drawing has been approved.."
			todo.reference_type = "Drawing"
			todo.reference_name = doc.name
			todo.project = None
			todo.role = None
			todo.assigned_by = doc.modified_by
			todo.assigned_by_full_name = frappe.get_value("User", doc.modified_by, "full_name")
			# Save and submit the ToDo document
			todo.insert(ignore_permissions=True)
			# todo.submit()
			frappe.db.commit()
			frappe.msgprint("ToDo created and submitted successfully.")

	except Exception as e:
		frappe.log_error(f"Error creating and submitting ToDo: {e}")






# Define a function to be executed on submission of the document
def create_todo_on_insert_pattern_doc(doc, method):
	try:
		# Check if the document is being submitted
		if doc.workflow_state == "Draft":
			# Create a new ToDo document
			todo = frappe.new_doc("ToDo")
			# Set the fields as per your requirements
			todo.status = "Open"
			todo.priority = "High"
			todo.todo_title = None
			todo.color = None
			todo.date = frappe.utils.today()
			todo.allocated_to = "vivekd@navyacustom.com"
			todo.allot_to_user = "vivekd@navyacustom.com"
			todo.full_name = "Vivek "
			todo.description = "Hey, This Pattern has been created.."
			todo.reference_type = "Pattern"
			todo.reference_name = doc.name
			todo.project = None
			todo.role = None
			todo.assigned_by = doc.modified_by
			todo.assigned_by_full_name = frappe.get_value("User", doc.modified_by, "full_name")
			print("##################################################################################################")
			# Save and submit the ToDo document
			todo.insert(ignore_permissions=True)
			# todo.submit()
			frappe.db.commit()
			frappe.msgprint("ToDo created and submitted successfully.")

	except Exception as e:
		frappe.log_error(f"Error creating and submitting ToDo: {e}")


