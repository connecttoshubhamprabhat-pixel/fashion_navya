import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, getdate, nowdate


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




@frappe.whitelist()
def make_se(source_name, target_doc=None):
	doclist = get_mapped_doc(
		"Supplier Quotation",
		source_name,
		{
			"Supplier Quotation": {
				"doctype": "Stock Entry",
				"field_map": {
					"name": "custom_supplier_quotation",
				},
			},
			"Supplier Quotation Item": {
				"doctype": "Stock Entry Detail",
				"field_map": [
					["custom_fg_item", "item_code"],
					["custom_fg_qty","qty"]

				],
			},
		},

	target_doc,
	)

	return doclist
