import frappe


@frappe.whitelist()
def only_take_kit_item(doc,method):
    """
        writing code to kit item
    """
    if doc.skip_validate==0:
        for item in doc.items:
            item_doc=frappe.get_doc("Item",item.item_code)
            if item_doc.has_variants==0 and item_doc.variant_of:
                frappe.throw("Sorry You can not take variant Item")
            
