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

                    if data_w[0]['actual_qty']>0:
                        if data_w[0]['actual_qty']<i.qty:
                            msg=" {}/row No:- {} Out of Stock".format(i.item_code,row)
                            frappe.throw(msg)
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


@frappe.whitelist()
def check_warehouse_wise_wrkflw(doc,method):
    user=frappe.session.user
    roles=frappe.get_roles(user)
    t_warehouse=[]
    stock_t_warehouse=[]
    sales_roles=['Sales Manager','Sales Team']
    stock_roles=['Stock Team','Manufacturing team']
    se=frappe.get_all("Permitted Files", filters ={'document_name':"Stock Entry"},fields = ['name'])
    if se:
        pfdoc=frappe.get_doc("Permitted Files",se[0]['name'])
        for i in doc.items:
            if i.t_warehouse=="SStore - NAVYA":
                t_warehouse.append(i.t_warehouse)
                
            else:
                stock_t_warehouse.append(i.t_warehouse)


        if t_warehouse:
            get_pf=frappe.db.sql(""" select location,role from `tabLocation Wise Warehoue` where docstatus=0 and warehouse='{}' and parent='{}'  """.format(t_warehouse[0],pfdoc.name),as_dict=1)
            if get_pf:
                if get_pf[0]['role'] not in sales_roles and get_pf[0]['location']=="Santushti":
                    frappe.throw("It will be receive by Sales team")
        
        if stock_t_warehouse:
            get_pf=frappe.db.sql(""" select location,role from `tabLocation Wise Warehoue` where docstatus=0 and warehouse='{}' and parent='{}'  """.format(stock_t_warehouse[0],pfdoc.name),as_dict=1)
            if get_pf:
                if get_pf[0]['role'] not in stock_roles  and get_pf[0]['location']=="Sainik Farms":
                    frappe.throw("It will be receive by Stock team")

