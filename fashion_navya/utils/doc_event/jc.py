import frappe


@frappe.whitelist()
def se_check_all(doc,method):
	if doc.work_order:
		get_se=frappe.db.sql("""select name from `tabStock Entry` where docstatus=1 and work_order='{}' and stock_entry_type="Material Transfer for Manufacture"   """.format(doc.work_order),as_dict=1)
		if len(get_se)==0:
			frappe.throw("""Stock Entry is not submitted   """)



@frappe.whitelist()
def se_check_all_jc(doc,method):
	if doc.work_order and not doc.get("__islocal"):
		get_se=frappe.db.sql("""select name from `tabStock Entry` where docstatus=1 and work_order='{}' and stock_entry_type="Material Transfer for Manufacture"   """.format(doc.work_order),as_dict=1)
		if len(get_se)==0:
			frappe.throw("""Stock Entry is not submitted   """)




@frappe.whitelist()
def set_validation_for_submit(doc,method):
	user=frappe.session.user
	admins=["pawasthy11@gmail.com"]
	get_id=frappe.db.sql(""" select branch from   `tabEmployee` where user_id='{}'  """.format(user),as_dict=1)
	if len(get_id)!=0 and user not in admins :
		if get_id[0]['branch']!=doc.custom_branch:
			frappe.throw("आपकी ब्रांच अलग है ,आप इसको Submit नहीं कर सकते (You can't submit)||")

