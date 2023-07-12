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
    get_pe=frappe.db.sql(""" select name from `tabPayment Entry` where payment_type="Internal Transfer" and docstatus=0  {} """.format(condition),as_dict=1)
    return get_pe
