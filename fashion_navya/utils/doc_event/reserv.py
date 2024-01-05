import frappe


@frappe.whitelist(allow_guest=True)
def reserve_stock_pos(doc,method):
	if doc.items:
		for i in doc.items:
			bin_entry = frappe.get_all("Bin", filters={"item_code":i.item_code}, fields=["actual_qty","reserved_qty"])
			total_actual=sum(bin['actual_qty'] for bin in bin_entry)
			total_res=sum(bin['reserved_qty'] for bin in bin_entry)
			remain=total_actual-total_res
			if remain==0 or remain<0:
				frappe.throw("Out of Stock")
