import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate

from erpnext.accounts.party import get_party_account
from erpnext.accounts.doctype.payment_order.payment_order import make_payment_records


@frappe.whitelist()
def create_jv_pay_oreders(name=None):
    if not name:
        return

    doc=frappe.get_doc("Payment Order",name)
    supplier_list=[]
    for i in doc.references:
        supplier_list.append(i.supplier)
    sup=list(set(supplier_list))
    for s in sup:
        make_payment_records(name=name,supplier=s)
        frappe.db.commit()
