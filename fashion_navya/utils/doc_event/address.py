import frappe

@frappe.whitelist()
def check_is_shipping(doc,method):
    if doc.address_type=="Shipping":
        doc.set("is_shipping_address",1)

    if doc.address_type=="Billing":
        doc.set("is_primary_address",1)

# @frappe.whitelist()
# def make_contact_for_addess():
#     get_address=frappe.db.sql("""select phone from  `tabAddress`
#  """)
