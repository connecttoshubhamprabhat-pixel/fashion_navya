import frappe
from frappe.utils import today
from frappe.utils import now
from frappe.utils import time_diff_in_hours,date_diff

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




@frappe.whitelist()
def check_date_hr_diff(doc,method):
	if doc.from_time and doc.to_time:
		f=str(doc.from_time).split(" ")
		ftime=f[1].split(":")
		t=str(doc.to_time).split(" ")
		ttime=t[1].split(":")
		fhour=int(ftime[0])
		fminute=int(ftime[1])
		thour=int(ttime[0])
		tminute=int(ttime[1])
		if thour==13:
			if tminute>10:
				frappe.throw("यह भोजन का समय है")
		if fhour==13:
			if 39>fminute:
				frappe.throw("आप 13:44 से पहले शुरू नहीं कर सकते")
		if 13>fhour and thour>13:
			frappe.throw("दोपहर के भोजन का समय नहीं जोड़ा जाना चाहिए")




@frappe.whitelist()
def check_date_hr_diff_ts(doc,method):
	if doc.without_source==1:
		return

	for i in doc.time_logs:
		f=str(i.from_time).split(" ")
		ftime=f[1].split(":")
		t=str(i.to_time).split(" ")
		ttime=t[1].split(":")
		fhour=int(ftime[0])
		fminute=int(ftime[1])
		thour=int(ttime[0])
		tminute=int(ttime[1])
		if thour==13:
			if tminute>10:
				frappe.throw("यह भोजन का समय है")
		if fhour==13:
			if 39>fminute:
				frappe.throw("आप 13:44 से पहले शुरू नहीं कर सकते")
		if 13>fhour and thour>13:
			frappe.throw("दोपहर के भोजन का समय नहीं जोड़ा जाना चाहिए")

