import frappe

#Bank slip deposite
@frappe.whitelist()
def fetch_per_pending(from_time=None,to_time=None):
    condition="  "
    if from_time and to_time:
        from_time=str(from_time)
        to_time=str(to_time)
        condition +="and posting_date between '{}' and '{}' ".format(from_time,to_time)

    print(condition,"from")
    get_pe=frappe.db.sql(""" select name from `tabPayment Entry` where posting_date>"2022-12-30"  and payment_type="Internal Transfer" and docstatus=0  {} """.format(condition),as_dict=1)
    return get_pe



@frappe.whitelist()
def submit_all_pe(doc,method):
    if doc.deposited_slip:
        for i in doc.deposited_slip:
            pe=frappe.get_doc("Payment Entry",i.payment_entry)
            pe.submit()


@frappe.whitelist(allow_guest=True)
def calculate_total_amount(doc,method):
    amount=0
    for i in doc.deposited_slip:
        amount +=i.amount

    doc.set("total_amount",0.0)
    doc.set("total_amount",amount)
