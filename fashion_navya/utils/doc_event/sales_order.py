import frappe
from erpnext.stock.dashboard.item_dashboard import get_data
from datetime import datetime
from frappe.utils import add_to_date
from frappe.utils import today
from frappe import utils

@frappe.whitelist()
def show_live_update(item=None,customer=None):
    if not item and not customer:
        return
    customer=customer
    today = datetime.now().strftime('%Y-%m-%d')
    data_warehouse=[]
    data_count=0
    santushti_stock_total=[0]
    customer_wo=[0]
    work_order_projected=[0]
    woc=frappe.db.sql(""" select name from `tabWork Order` where production_item='{}' and docstatus=1 and status='In Process'  """.format(item),as_dict=1)
    if len(woc)!=0:
        if woc[0]['name']!=None:
            customer_wo.append(len(woc))

    shop_name=['Santushti - NAVYA']
    # wo_draft=frappe.db.sql(""" select name from `tabWork Order` where production_item='{}' and docstatus=1 and status='In Process'  and sales_order is null """.format(item),as_dict=1)
    # if len(wo_draft)!=0:
    #     if wo_draft[0]['name']!=None:
    #         work_order_projected.append(1)


    child_list_santushti=[]
    get_all_childs=frappe.db.sql(""" select name from `tabWarehouse` where parent_warehouse='{}' and disabled=0   """.format('Santushti - NAVYA'),as_dict=1)
    if get_all_childs:
        for wc in get_all_childs:
            child_list_santushti.append(wc['name'])

    if child_list_santushti:
        for wc1 in child_list_santushti:
            data=get_data(item_code=item,warehouse=wc1)
            if data and wc1!="SCustomer Rack - NAVYA":
                for wc2 in data:
                    if int(wc2['actual_qty'])>0:
                        santushti_stock_total.append(int(wc2['actual_qty']))
    # print(santushti_stock_total,'santushti_stock_total')
    # print(customer_wo,'customer_wo')
    # print(work_order_projected,'work_order_projected')
    # print(customer_wo,'customer_wo')

    check_stock_other=[0]

    if sum(santushti_stock_total)!=0:
        date_today=utils.today()
        #frappe.throw("Please handle by POS")
        return date_today,"POS"





    if sum(santushti_stock_total)==0:
        print('zero')
        stock_other=[0]
        data=get_data(item_code=item)
        if len(data)!=0:
            for wq in data:
                if int(wq['actual_qty']) >0:
                    stock_other.append(int(wq['actual_qty']))
        if sum(stock_other)>0:
            check_stock_other.append(1)
            after_3_days = add_to_date(datetime.now(), days=3, as_string=True)
            #i.db_set("delivery_date",after_3_days, update_modified=False)
            return after_3_days,"Post-Order"
    if sum(customer_wo) >0:
        after_12_days = add_to_date(datetime.now(), days=12, as_string=True)
        #i.db_set("delivery_date",after_12_days, update_modified=False)
        return after_12_days,'Short-Order'


    if sum(customer_wo)==0:
        after_26_days = add_to_date(datetime.now(), days=26, as_string=True)
        #i.db_set("delivery_date",after_26_days, update_modified=False)
        return after_26_days,'Pre-Order'







@frappe.whitelist()
def make_se_transfer(doc,method):
    shop_name_list=["Santushti"]
    if not frappe.db.exists("Warehouse","SStore - NAVYA"):
        return
    all_dt_orders=[]
    for i  in doc.items:
        all_dt_orders.append(i.delivery_order)

    all_dt_orders_rm_duplicate=list(set(all_dt_orders))
    if len(all_dt_orders_rm_duplicate)>1:
        for item in doc.items:
            if item.delivery_order=="Post-Order":
                d={"doctype":"Stock Entry","rfse":"By System","stock_entry_type":"Material Transfer"}
                se_doc=frappe.get_doc(d)
                row = se_doc.append("items", {})
                row.item_code=item.item_code
                row.qty=item.qty
                get_datas=get_data(item_code=item.item_code)
                source_warehouse=[]
                if len(get_datas)!=0 and not source_warehouse :
                    for m in get_datas:
                        if m['actual_qty']>=item.qty:
                            source_warehouse.append(m['warehouse'])
                            break
                if not source_warehouse:
                    continue
                if source_warehouse:
                    row.s_warehouse=source_warehouse[0]
                    if doc.shop_name=="Santushti":
                        row.t_warehouse="SStore - NAVYA"

                try:
                    se_doc.insert(ignore_permissions=True)
                except:
                    frappe.msgprint("An error occurred during the creation of the stock entry.")
                    pass








    else:
        d={"doctype":"Stock Entry","rfse":"By System","stock_entry_type":"Material Transfer"}
        se_doc=frappe.get_doc(d)
        check_insert=[]
        for item in doc.items:
            if item.delivery_order=="Post-Order":
                row = se_doc.append("items", {})
                row.item_code=item.item_code
                row.qty=item.qty
                get_datas=get_data(item_code=item.item_code)
                source_warehouse=[]
                if len(get_datas)!=0 and not source_warehouse :
                    for m in get_datas:
                        if m['actual_qty']>=item.qty:
                            check_insert.append("yes")
                            source_warehouse.append(m['warehouse'])
                            break
                if not source_warehouse:
                    continue
                if source_warehouse:
                    row.s_warehouse=source_warehouse[0]
                    if doc.shop_name=="Santushti":
                        row.t_warehouse="SStore - NAVYA"

        try:
            if check_insert:
                se_doc.insert(ignore_permissions=True)
        except:
            frappe.msgprint("An error occurred during the creation of the stock entry.")
            pass




@frappe.whitelist()
def make_workorder_pre(doc,method):
    for i in doc.items:
        if i.delivery_order=="Pre-Order":
            d={"doctype":"Work Order","production_item":i.item_code,"qty":2}
            get_bom=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and is_active=1 and is_default=1  and item='{}' """.format(i.item_code),as_dict=1)
            if not get_bom:
                msg="Sorry BOM is not created for Row no: {} Line Item".format(i.idx)
                frappe.msgprint(msg)
                continue
            if get_bom:
                if get_bom[0]['name']!=None:
                    d['bom_no']=get_bom[0]['name']
                    d['sales_order']=doc.name
                    if doc.delivery_type=="Courier":
                        if frappe.db.exists("Warehouse","Courier Station - NAVYA"):
                            d['fg_warehouse']="Courier Station - NAVYA"
                            d['scrap_warehouse']="Courier Station - NAVYA"

                    if doc.delivery_type=="Will come for trial":
                        if frappe.db.exists("Warehouse","Navya Finish Product RACK-4 - NAVYA") and frappe.db.exists("Warehouse","Navya Finish Product RACK-4 - NAVYA"):
                            if doc.delivery_location in ['Sainik Farm','From Sainik Farm']:
                                d["fg_warehouse"]="Navya Finish Product RACK-4 - NAVYA"
                                d["scrap_warehouse"]="Navya Finish Product RACK-4 - NAVYA"

                            if doc.delivery_location in ['Santushti','From Santushti']:
                                d["fg_warehouse"]="Srack4 - NAVYA"
                                d["scrap_warehouse"]="Srack4 - NAVYA"


                    wodoc=frappe.get_doc(d)
                    try:
                        wodoc.insert(ignore_permissions=True)
                        msg2="Work order {} is Created for row no {} Line Item".format(wodoc.name,i.idx)
                        frappe.msgprint(msg2)
                    except:
                        frappe.msgprint("An error occurred during the creation of the Work Order.")
                        pass
