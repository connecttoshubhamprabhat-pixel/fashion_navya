import frappe

@frappe.whitelist()
def check_lunch_time(doc,method):

	if doc.without_source:
		return
	get_shift=frappe.db.sql(""" select name,start_time,end_time from `tabShift Type` where name="Lunch"   """,as_dict=1)
	if len(get_shift)==0:
		frappe.msgprint("Shift Type missing")
		return

	start_time=str(get_shift[0]['start_time'])
	end_time=str(get_shift[0]['end_time'])
	start_min=start_time.split(":")
	end_time_min=end_time.split(":")
	for i in doc.time_logs:
		if i.from_time and not i.to_time:
			split_f=str(i.from_time).split(" ")
			get_min=split_f[-1]
			split_min=get_min.split(":")
			if int(start_min[0])==int(split_min[0]):
				if 39>=int(split_min[1]) >=5:
					frappe.throw("Sorry Lunch Time")

			if int(end_time_min[0])==int(split_min[0]):
				if 39>=int(split_min[1]) >=5:
					frappe.throw("Sorry Lunch Time")

		if i.from_time and  i.to_time:
			split_f=str(i.to_time).split(" ")
			get_min=split_f[-1]
			split_min=get_min.split(":")
			if int(start_min[0])==int(split_min[0]):
				if 39>=int(split_min[1]) >=5:
					frappe.throw("Sorry Lunch Time")
			if int(end_time_min[0])==int(split_min[0]):
				if 39>=int(split_min[1]) >=5:
					frappe.throw("Sorry Lunch Time")


@frappe.whitelist()
def office_time_start_end(doc,method):
	if doc.without_source==1:
		return

	for i in doc.time_logs:
		if i.from_time and not i.to_time:
			split_f=str(i.from_time).split(" ")
			get_min=split_f[-1]
			split_min=get_min.split(":")
			if int(split_min[0])==9:
				if int(split_min[1])<30:
					frappe.throw("Sorry,You cannot start before 9:30")





@frappe.whitelist()
def job_card(doc,method):
	jc=[]
	if doc.job_card:
		jcdoc=frappe.get_doc("Job Card",doc.job_card)
		if jcdoc.status=="Completed":
			frappe.throw("Sorry Job card is completed")
