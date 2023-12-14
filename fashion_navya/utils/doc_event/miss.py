import frappe
from frappe.utils import time_diff_in_hours

@frappe.whitelist()
def add_total_hours(doc,method):
	total=time_diff_in_hours(doc.to_time,doc.from_time)
	doc.set("total_hours",total)


@frappe.whitelist()
def add_total_hours_old():
	get_all=frappe.db.sql("""select name from `tabTimesheet Missing` where docstatus=1  """,as_dict=1)
	for i in get_all:
		doc=frappe.get_doc("Timesheet Missing",i['name'])
		total=time_diff_in_hours(doc.to_time,doc.from_time)
		frappe.db.sql("""update `tabTimesheet Missing` set total_hours='{}' where name='{}'  """.format(total,doc.name))
		frappe.db.commit()
