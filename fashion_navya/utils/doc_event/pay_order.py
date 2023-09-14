import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate

from erpnext.accounts.party import get_party_account
from erpnext.accounts.doctype.payment_request.payment_request import make_payment_entry
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

@frappe.whitelist()
def make_payment_entry(docname=None):
    if not docname:
        return
    paydoc=frappe.get_doc("Payment Order",docname)
    exists_pe=frappe.db.sql(""" select name from `tabPayment Entry` and docstatus=1 and payment_order='{}' """.format(paydoc.name),as_dict=1)
    if len(exists_pe)!=0:
        frappe.throw("Already Payment created")
    pe_request=[]
    for i in paydoc.references:
        pe_request.append(i.payment_request)

    created=[]
    if pe_request:
        for p in pe_request:
            doc = frappe.get_doc("Payment Request",p)
            pe_docs=doc.create_payment_entry(submit=True).as_dict()
            if pe_docs.get("name"):
                made_pe=frappe.get_doc("Payment Entry",pe_docs.get("name"))
                made_pe.db_set("payment_order",docname, update_modified=False)
                made_pe.db_set("reference_no",paydoc.reference_no, update_modified=False)
                made_pe.db_set("reference_date",paydoc.reference_date, update_modified=False)
            frappe.db.commit()
            created.append("yes")

    if created:
        frappe.msgprint("Payment Entry is created")
        doc.reload()




@frappe.whitelist(allow_guest=True)
def calculate_total_amount(doc,method):
    amount=0
    for i in doc.references:
        amount +=i.amount


    doc.set("total_amount",0.0)
    doc.set("total_amount",amount)
