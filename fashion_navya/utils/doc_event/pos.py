import frappe


@frappe.whitelist()
def check_discount(doc,method):
    if doc.additional_discount_percentage:
        total=0
        for i in doc.items:
            item=frappe.get_doc("Item",i.item_code)
            total+=item.max_discount
            
        if doc.additional_discount_percentage>total:
            msg="the discount should not be more than {}".format(total)
            frappe.throw(msg)



@frappe.whitelist()
def check_for_sample(doc,method):
	if doc.items:
		for i in doc.items:
			item=frappe.get_doc("Item",i.item_code)
			if item.item_group=="Sample":
				frappe.throw("Sample is not for Sale")
