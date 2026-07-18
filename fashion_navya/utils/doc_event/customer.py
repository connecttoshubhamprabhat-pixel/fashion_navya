import frappe
import re
from frappe.contacts.doctype.contact.test_contact import create_contact


@frappe.whitelist()
def customer_no_check_exists(doc,method):
	if doc.cnumber:
		no_exists=frappe.db.sql(""" select name from `tabCustomer` where cnumber='{}' and name!='{}'  """.format(doc.cnumber,doc.name),as_dict=1)
		# if len(no_exists)!=0:
		# 	frappe.throw("Number Already Exists")



@frappe.whitelist()
def create_contact(doc,method):
	no=doc.cnumber
	if no:
		d=re.findall(r'\d+',no)
		num="".join(d)
		c={"doctype":"Contact","first_name":doc.name,"status":"Open"}
		c['salutation']=doc.salutation
		c['whatsapp_no']=num
		#d["activate_whatsapp"]=1
		contact=frappe.get_doc(c)
		row=contact.append("phone_nos", {})
		row.phone=num
		row.is_primary_phone=1
		row.is_whatsapp_number=1
		#make link
		link=contact.append("links",{})
		link.link_doctype="Customer"
		link.link_name=doc.name


		try:
			contact.insert(ignore_permissions=True)
			c=0
			if contact.whatsapp_no and contact.activate_whatsapp==0:
				contact.db_set("activate_whatsapp",1, update_modified=False)
			if c==1:
				contact.save(ignore_permissions=True)
		except:
			pass
		#frappe.msgprint("Contact is created successfully")


@frappe.whitelist()
def contact_update(doc,method):
	try:
		if not doc.get("__islocal"):
			old=doc.get_doc_before_save()
			d=re.findall(r'\d+',old.cnumber)
			old_num="".join(d)
			dn=re.findall(r'\d+',doc.cnumber)
			new_num="".join(dn)
			if old_num!=new_num:
				frappe.db.sql("""update `tabContact Phone`  set phone='{}'  ,is_whatsapp_number=1  where idx=1 and parent in (select parent from `tabDynamic Link` where link_doctype="Customer" and link_name='{}') """.format(new_num,doc.name))
				frappe.db.sql("""update `tabContact`  set phone='{}'   where name in (select parent from `tabDynamic Link` where link_doctype="Customer" and link_name='{}') """.format(new_num,doc.name))
				frappe.db.sql("""update `tabContact`  set whatsapp_no='{}'    where name in (select parent from `tabDynamic Link` where link_doctype="Customer" and link_name='{}') """.format(new_num,doc.name))
				frappe.db.commit()
	except:
		pass
