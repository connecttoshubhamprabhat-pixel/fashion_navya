import frappe
import datetime
import json
from frappe.utils import date_diff

@frappe.whitelist()
def qty_check_jc(doc,method):
	total_completed=[0]
	for i in doc.time_logs:
		total_completed.append(i.completed_qty)

	if doc.for_quantity!=sum(total_completed):
		frappe.throw("Qty To Manufacture and Completed qty are not same")

@frappe.whitelist()
def check_work_order_status(doc,method):
	pass




#job card time logs
@frappe.whitelist()
def make_timesheet_all(doc,method):

	if doc.time_logs:
		for i in doc.time_logs:
			dif=float(date_diff(str(i.to_time),str(i.from_time)))
			from_time=str(i.from_time).split()
			d={"doctype":"Timesheet","start_date":from_time[0]}
			d['end_date']=from_time[0]
			d['employee']=i.employee
			d['source_type']="Job Card"
			d['job_card']=i.parent
			d['total_hours']=dif
			ts=frappe.get_doc(d)
			row = ts.append("time_logs", {})
			row.from_time=i.from_time
			row.to_time=i.to_time
			row.completed=1
			row.hours=dif
			row.job_card=i.parent
			row.activity_type="Execution"
			try:
				ts.save(ignore_permissions=True)
				ts.submit()
			except:
				pass


def time_logs_into_timesheets(doc, method):
	if method == "on_submit" and doc.doctype == "Job Card" and doc.docstatus == 1:
		for log in doc.time_logs:
			dif=log.time_in_mins/60
			timesheet = frappe.new_doc("Timesheet")
			timesheet.update({
                		    "start_date": str(log.from_time),
                		    "end_date": str(log.to_time),
                		    "employee": log.employee,
                		    "source_type": "Job Card",
                		    "job_card": doc.name,
                		    "total_hours": dif
            		    })

			timesheet.append("time_logs", {
                		    "from_time": str(log.from_time),
                		    "to_time": str(log.to_time),
                		    "completed": 1,
                		    "hours": dif,
                		    "job_card": doc.name,
                		    "activity_type": "Execution"


                            })

			try:
				timesheet.insert(ignore_permissions=True)
				timesheet.submit()

			except Exception as e:
				frappe.log_error(f"Error creating timesheet for Job Card {doc.name}: {e}")
