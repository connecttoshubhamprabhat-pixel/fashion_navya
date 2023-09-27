import frappe
from datetime import datetime # from python std library
from frappe.utils import add_to_date



@frappe.whitelist()
def make_payment_system(name=None):
	today = datetime.now().strftime('%Y-%m-%d')
	if not name:
		return
	get_pe=frappe.db.sql("""select name from `tabPayment Entry` where docstatus=1 and payment_imprest='{}'  """.format(name),as_dict=1)
	if len(get_pe)==0:
		doc=frappe.get_doc("Payment Imprest",name)
		d={"doctype":"Payment Entry","mode_of_payment":"Cash"}
		d['payment_type']="Internal Transfer"
		d['paid_to']="Kundan- imprest for purchase - NAVYA"
		d['paid_from']="1102010203 - STATE BANK OF INDIA - NAVYA"
		d['received_amount']=doc.total_amount
		d['automated']=1
		d['reference_no']=doc.name
		d['reference_date']=today
		d['payment_imprest']=doc.name
		d['paid_amount']=doc.total_amount
		pe_new=frappe.get_doc(d)
		pe_new.insert()
		#pe_new.submit()
		frappe.msgprint("Payment Created")
	else:
		frappe.msgprint("Already Created")
