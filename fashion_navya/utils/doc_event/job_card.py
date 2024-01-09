import frappe


@frappe.whitelist()
def qty_check_jc(doc,method):
	total_completed=[0]
	for i in doc.time_logs:
		total_completed.append(i.completed_qty)

	if doc.for_quantity!=sum(total_completed):
		frappe.throw("Qty To Manufacture and Completed qty are not same")
