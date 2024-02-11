import frappe


#setup is urgent task
@frappe.whitelist(allow_guest=True)
def set_is_urgent_task(doc,method):
    if doc.is_urgent==1:
        frappe.db.sql("""update `tabTask` set is_urgent=1 where is_urgent=0 and project='{}'  """.format(doc.name))
        frappe.db.commit()
        
    if doc.is_urgent==0:
        frappe.db.sql("""update `tabTask` set is_urgent=0 where is_urgent=1 and project='{}'  """.format(doc.name))
        frappe.db.commit()