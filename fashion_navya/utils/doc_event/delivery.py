import frappe
from datetime import datetime, timedelta


@frappe.whitelist()
def set_notify_todo():
	days=[]
	now = datetime.now()
	for x in range(7):
		d = now - timedelta(days=-x)
		print(str(d.strftime("%Y-%m-%d")))
		days.append(str(d.strftime("%Y-%m-%d")))

	#days=["2023-08-13"]
	for d in days:
		get_wo=frappe.db.sql(""" select name from `tabWork Order` where docstatus < 2 and expected_delivery_date='{}'  """.format(d),as_dict=1)
		if len(get_wo)!=0:
			#print('ert')
			for i in  get_wo:
				print(i['name'],'wo')
				d={'doctype':"ToDo","priority":"High","reference_type":"Work Order"}
				des="The delivery for this Work Order is due soon.(इस वर्क ऑर्डर की डिलीवरी जल्द ही होने वाली है।)"
				d['description']=des
				d['reference_name']=i['name']
				d['assigned_by']="amita@navya.biz"
				user_list=['kundan@navyacustom.com',"sujeets@navyacustom.com"]
				for j in user_list:
					get_ref=frappe.db.sql(""" select name from `tabToDo` where allocated_to='{}' and reference_name='{}' and status="Open"  """.format(j,i['name']),as_dict=1)
					if len(get_ref)==0:
						#print(123)
						d['allocated_to']=j
						doc=frappe.get_doc(d)
						try:
							doc.insert()
							frappe.db.commit()
						except:
							continue

