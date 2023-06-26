import frappe
from erpnext.stock.dashboard.item_dashboard import get_data
from datetime import datetime
from frappe.utils import add_to_date
from frappe.utils import today

@frappe.whitelist()
def show_live_update(item=None,customer=None):
    if not item and not cutomer:
        return
    customer=customer
    today = datetime.now().strftime('%Y-%m-%d')
    data_warehouse=[]
    data_count=0
    santushti_stock_total=[0]
    customer_wo=[0]
    work_order_projected=[0]
    if customer:
        woc=frappe.db.sql(""" select name from `tabWork Order` where production_item='{}' and docstatus < 2 and status='In Process' and customer='{}' """.format(item,customer),as_dict=1)
        if len(woc)!=0:
            if woc[0]['name']!=None:
                customer_wo.append(len(woc))

    shop_name=['Santushti - NAVYA']
    wo_draft=frappe.db.sql(""" select name from `tabWork Order` where production_item='{}' and docstatus < 2 and status='In Process'  and sales_order is null """.format(item),as_dict=1)
    if len(wo_draft)!=0:
        if wo_draft[0]['name']!=None:
            work_order_projected.append(1)


    child_list_santushti=[]
    get_all_childs=frappe.db.sql(""" select name from `tabWarehouse` where parent_warehouse='{}' and disabled=0   """.format('Santushti - NAVYA'),as_dict=1)
    if get_all_childs:
        for wc in get_all_childs:
            child_list_santushti.append(wc['name'])

    if child_list_santushti:
        for wc1 in child_list_santushti:
            data=get_data(item_code=item,warehouse=wc1)
            if data:
                for wc2 in data:
                    santushti_stock_total.append(int(wc2['actual_qty']))
    print(santushti_stock_total,'santushti_stock_total')
    print(customer_wo,'customer_wo')
    print(work_order_projected,'work_order_projected')
    print(customer_wo,'customer_wo')

    check_stock_other=[0]
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
            return after_3_days
    if sum(customer_wo) >0:
        after_12_days = add_to_date(datetime.now(), days=12, as_string=True)
        #i.db_set("delivery_date",after_12_days, update_modified=False)
        return after_12_days

    if sum(work_order_projected)>0:
        after_12_days = add_to_date(datetime.now(), days=12, as_string=True)
        #i.db_set("delivery_date",after_12_days, update_modified=False)

        return after_12_days

    if sum(customer_wo)==0 and len(work_order_projected)==0:
        after_26_days = add_to_date(datetime.now(), days=26, as_string=True)
        #i.db_set("delivery_date",after_26_days, update_modified=False)
        return after_26_days

    if sum(customer_wo)==0 and sum(work_order_projected)==0 and sum(check_stock_other)==0:
        after_26_days = add_to_date(datetime.now(), days=26, as_string=True)
        return after_26_days

