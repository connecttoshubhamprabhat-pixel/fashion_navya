import frappe
from frappe.utils import today
from frappe.utils import now
from frappe.utils import time_diff_in_hours

#aug/19/23
@frappe.whitelist()
def submit_lunch_time():
	tdate=str(today())
	dtime=str(now())
	ts=frappe.db.sql("""select name from `tabTimesheet` where start_date='{}' and docstatus=0   """.format(tdate),as_dict=1)
	if len(ts)!=0:
		for i in ts:
			doc=frappe.get_doc("Timesheet",i['name'])
			hours=time_diff_in_hours(dtime,doc.time_logs[0].from_time)
			td.set("to_time",to_time_now)
			td.set("completed",1)
			td.set("source_type","scheduled")
			td.set("hours",float(hours))

