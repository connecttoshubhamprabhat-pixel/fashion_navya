import frappe
import json
from dateutil.relativedelta import relativedelta
from frappe import _
from frappe.utils import (
	cint,
	date_diff,
	flt,
	get_datetime,
	get_link_to_form,
	getdate,
	nowdate,
	time_diff_in_hours,
)
from pypika import functions as fn


@frappe.whitelist()
def make_job_card(work_order, operations=None):
	#frappe.throw('aaaaa')
	operations=[]
	work_order = frappe.get_doc("Work Order", work_order)
	if len(work_order.operations)!=0:
		for m in work_order.operations:
			if m.completed_qty==0:
			
				d={}
				d['name']=m.name
				d['operation']=m.operation
				d['workstation']=m.workstation
				d['qty']=1
				d['pending_qty']=1
				d['batch_size']=1
				d['idx']=m.idx
				d['__checked']=1
				d['job_card_qty']=1
				operations.append(d)


	for row in operations:
		row = frappe._dict(row)
		print(row)
		validate_operation_data(row)
		qty = row.get("qty")
		while qty > 0:
			qty = split_qty_based_on_batch_size(work_order, row, qty)
			if row.job_card_qty > 0:
				print('aaaaaaaa')
				create_job_card(work_order, row, auto_create=True)






def create_job_card(work_order, row, enable_capacity_planning=False, auto_create=False):
	doc = frappe.new_doc("Job Card")
	doc.update(
		{
			"work_order": work_order.name,
			"workstation_type": row.get("workstation_type"),
			"operation": row.get("operation"),
			"workstation": row.get("workstation"),
			"posting_date": nowdate(),
			"for_quantity": row.job_card_qty or work_order.get("qty", 0),
			"operation_id": row.get("name"),
			"bom_no": work_order.bom_no,
			"project": work_order.project,
			"company": work_order.company,
			"sequence_id": row.get("sequence_id"),
			"wip_warehouse": work_order.wip_warehouse,
			"hour_rate": row.get("hour_rate"),
			"serial_no": row.get("serial_no"),
		}
	)

	if work_order.transfer_material_against == "Job Card" and not work_order.skip_transfer:
		doc.get_required_items()

	if auto_create:
		doc.flags.ignore_mandatory = True
		if enable_capacity_planning:
			doc.schedule_time_logs(row)

		doc.insert()
		# row = doc.append("employee", {})
		# row.employee="HR-EMP-00009"
		logss= doc.append("time_logs", {})
		logss.from_time="2023-06-16 13:17:00"
		logss.to_time="2023-06-16 13:17:01"
		logss.employee="HR-EMP-00009"
		#logss.completed_qty=1
		doc.submit()


def validate_operation_data(row):
	if row.get("qty") <= 0:
		frappe.throw(
			_("Quantity to Manufacture can not be zero for the operation {0}").format(
				frappe.bold(row.get("operation"))
			)
		)

	if row.get("qty") > row.get("pending_qty"):
		frappe.throw(
			_("For operation {0}: Quantity ({1}) can not be greter than pending quantity({2})").format(
				frappe.bold(row.get("operation")),
				frappe.bold(row.get("qty")),
				frappe.bold(row.get("pending_qty")),
			)
		)

def split_qty_based_on_batch_size(wo_doc, row, qty):
	if not cint(
		frappe.db.get_value("Operation", row.operation, "create_job_card_based_on_batch_size")
	):
		row.batch_size = row.get("qty") or wo_doc.qty

	row.job_card_qty = row.batch_size
	if row.batch_size and qty >= row.batch_size:
		qty -= row.batch_size
	elif qty > 0:
		row.job_card_qty = qty
		qty = 0

	#get_serial_nos_for_job_card(row, wo_doc)

	return qty


# def get_serial_nos_for_job_card(row, wo_doc):
# 	if not wo_doc.serial_no:
# 		return

# 	serial_nos = get_serial_nos(wo_doc.serial_no)
# 	used_serial_nos = []
# 	for d in frappe.get_all(
# 		"Job Card",
# 		fields=["serial_no"],
# 		filters={"docstatus": ("<", 2), "work_order": wo_doc.name, "operation_id": row.name},
# 	):
# 		used_serial_nos.extend(get_serial_nos(d.serial_no))

# 	serial_nos = sorted(list(set(serial_nos) - set(used_serial_nos)))
# 	row.serial_no = "\n".join(serial_nos[0 : cint(row.job_card_qty)])


@frappe.whitelist()
def submit_js(name=None):
	alls=frappe.db.sql(""" select name from `tabJob Card` where docstatus=0 and work_order='{}' """.format(name),as_dict=1)
	if len(alls)!=0:
		for i in alls:
			jdoc=frappe.get_doc("Job Card",i['name'])
			if jdoc.docstatus==0:
				jdoc.set("total_conpleted_qty",1)
				jdoc.time_logs=[]
				# r = jdoc.append("employee", {})
				# r.employee="HR-EMP-00009"
				

				row= jdoc.append("time_logs", {})
				row.from_time="2023-06-16 13:17:00"
				row.to_time="2023-06-16 13:19:04"
				row.employee="HR-EMP-00009"
				row.completed_qty=1
				jdoc.submit()
				frappe.db.commit()




@frappe.whitelist()
def check_item_no_subo(doc,method):
	if doc.production_item and doc.skip==0:
		getsubo=frappe.db.sql(""" select parent from `tabSubcontracting Order Item` where docstatus <2 and item_code='{}'  """.format(doc.production_item),as_dict=1)
		if len(getsubo)!=0:
			frappe.throw("it appears to belong subcontracting item")
