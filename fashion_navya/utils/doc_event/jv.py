import frappe


@frappe.whitelist()
def jv_refund_check(doc,method):
	if not doc.get("__islocal") and doc.jve=="Refund  for Customer":
		if not doc.payment_entry:
			frappe.throw("Payment Entry is required")

		getref=frappe.db.sql("""select reference_doctype,reference_name from `tabPayment Entry Reference` where docstatus=1 and parent='{}'  """.format(doc.payment_entry),as_dict=1)
		if len(getref)!=0:
			if getref[0]['reference_doctype']=="Sales Invoice":
				si=frappe.get_doc("Sales Invoice",getref[0]['reference_name'])
				get_delivery=frappe.db.sql("""select parent from `tabDelivery Note Item` where docstatus<2 and  against_sales_invoice='{}'  """.format(getref[0]['reference_name']),as_dict=1)
				if len(get_delivery)!=0:
					frappe.throw("Sorry first Delivery Note should be cancelled ")
				if si.docstatus<2:
					frappe.throw("Sales Invoice should be cancelled")
			if getref[0]['reference_doctype']=="Sales Order":
				so=frappe.get_doc("Sales Order",getref[0]['reference_name'])
				if so.docstatus<2:
					frappe.throw("Sales Order should be cancelled")
