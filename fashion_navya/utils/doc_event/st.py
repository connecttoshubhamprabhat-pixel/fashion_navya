import frappe

@frappe.whitelist()
def remove_serial_no(doc,method):
	if not doc.get("__islocal"):
		for i in doc.items:
			if i.serial_no:
				i.set("serial_no",None)
