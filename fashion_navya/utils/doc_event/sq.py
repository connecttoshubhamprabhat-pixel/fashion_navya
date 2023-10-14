import frappe


@frappe.whitelist()
def fetch_job_card(doc,method):
	mr=doc.items[0].material_request
	if mr:
		m=frappe.get_doc("Material Request",mr)
		doc.set("custom_job_card",m.job_card)
		doc.set("custom_work_order",m.work_order)


@frappe.whitelist()
def fetch_job_card_po(doc,method):
	mr=doc.items[0].material_request
	if mr:
		m=frappe.get_doc("Material Request",mr)
		doc.set("job_card",m.job_card)
		doc.set("work_order",m.work_order)


