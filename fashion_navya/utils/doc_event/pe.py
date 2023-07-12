import frappe


#jul 12/2023
@frappe.whitelist()
def create_pe_for_internal(doc,method):
    if doc.payment_type=="Receive":
        d={"doctype":"Payment Entry","mode_of_payment":"Cash"}
        d['payment_transfer']="Cash to Bank"
        d['payment_type']="Internal Transfer"
        d['paid_to']="1102010203 - STATE BANK OF INDIA - NAVYA"
        d['paid_from']=doc.paid_to
        d['received_amount']=doc.paid_amount
        d['reference_no']=doc.name
        d['customer_pe']=doc.name
        d['paid_amount']=doc.paid_amount
        pe_new=frappe.get_doc(d)
        pe_new.insert()


@frappe.whitelist()
def cancel_pe_cash(doc,method):
    if not  doc.customer_pe:
        pe_old=frappe.db.sql("""select name from `tabPayment Entry` where docstatus <2 and customer_pe='{}'  """.format(doc.name),as_dict=1)
        if len(pe_old)!=0:
            customer_pe=pe_old[0]['name']
            docpe=frappe.get_doc("Payment Entry",customer_pe)
            if docpe.docstatus==0:
                docpe.delete()
                frappe.db.commit()

            if docpe.docstatus==1:
                docpe.cancel()
                frappe.db.commit()
