import frappe
from erpnext.stock.dashboard.item_dashboard import get_data


@frappe.whitelist()
def warehouse_check_se(doc,method):
    if not doc.get("__islocal"):
        for i in doc.items:
            row=i.idx
            if doc.stock_entry_type in ["Material Transfer for Manufacture","Material Transfer"]:
                data_w=get_data(item_code=i.item_code,warehouse=i.s_warehouse)
                if len(data_w)!=0:
                    if data_w[0]['actual_qty']<0:
                        msg=" {}/row No:- {} Out of Stock".format(i.item_code,row)
                        frappe.throw(msg)
                    #if data_w[0]['actual_qty']>0:
                        #if data_w[0]['actual_qty']>i.qty:
                         #   msg=" {}/row No:- {} Out of Stock".format(i.item_code,row)
                          #  frappe.throw(msg)
                else:
                    msg=" {}/row No:- {} Out of Stock".format(i.item_code,row)
                    frappe.throw(msg)




@frappe.whitelist()
def check_work_flow(doc,method):
    if doc.stock_entry_type in ['Material Transfer for Manufacture','Manufacture','Material Transfer'] and  not doc.get("__islocal"):
        olddoc=doc.get_doc_before_save()
        user=frappe.session.user
        if olddoc.workflow_state in ['Authorised','Received']:
            print(olddoc.workflow_state,'olddoc.workflow_state')
            if olddoc.workflow_state=="Authorised" and doc.workflow_state=="Received":
                if olddoc.owner==user:
                    print(olddoc.owner,doc.owner)
                    msg="Sorry You cannot proceed,because If you have authorised this Record then you can not receive ."
                    frappe.throw(msg)
