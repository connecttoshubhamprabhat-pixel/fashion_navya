import frappe
from erpnext.stock.dashboard.item_dashboard import get_data
from datetime import datetime
from frappe.utils import add_to_date
from frappe.utils import today

@frappe.whitelist()
def show_live_update(doc,method):
    customer=doc.customer
    today = datetime.now().strftime('%Y-%m-%d')
    for i in doc.items:
        item=i.item_code
        data_warehouse=[]
        data_count=0
        santushti_stock_total=[0]
        customer_wo=[0]
        if customer:
            woc=frappe.db.sql(""" select name from `tabWork Order` where production_item='{}' and docstatus < 2 and status in ('Not Started','In Process','Draft') and customer='{}' """.format(item,customer),as_dict=1)
            if len(woc)!=0:
                customer_wo.append(len(woc))

        shop_name=['Santushti - NAVYA']
        wo_draft=frappe.db.sql(""" select name from `tabWork Order` where production_item='{}' and docstatus < 2 and status in ('Not Started','In Process','Draft')  and sales_order is null """.format(item),as_dict=1)
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
        if sum(santushti_stock_total)>0:
            i.db_set("delivery_date",today, update_modified=False)
            continue
        if sum(santushti_stock_total)==0:
            stock_other=[]
            data=get_data(item_code=item)
            if len(data)!=0:
                for wq in data:
                    stock_other.append(int(wq['actual_qty']))
                after_4_days = add_to_date(datetime.now(), days=4, as_string=True)
                i.db_set("delivery_date",after_4_days, update_modified=False)
                continue
        if sum(customer_wo) >0 or len(wo_draft)>0:
            after_12_days = add_to_date(datetime.now(), days=12, as_string=True)
            i.db_set("delivery_date",after_12_days, update_modified=False)
            continue

        if sum(customer_wo)==0 and len(wo_draft)==0:
            after_26_days = add_to_date(datetime.now(), days=26, as_string=True)
            i.db_set("delivery_date",after_26_days, update_modified=False)
            continue
