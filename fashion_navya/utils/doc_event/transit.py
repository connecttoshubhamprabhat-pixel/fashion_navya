import frappe


@frappe.whitelist(allow_guest=True)
def check_transit_entry(doc,method):
    stock_entry_type=['Material Transfer']
    if doc.add_to_transit and doc.ignore_custom==0 and doc.stock_entry_type in stock_entry_type and not doc.outgoing_stock_entry:
        for i in doc.items:
            if i.s_warehouse=="Default Transit - NAVYA":
                frappe.throw("It is not part of the End Transit Entry,So please change the source warehouse")
            transit_stock=[0]
            actual_qty=[0]
            draft_stock=[0]
            get_bin=frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code='{}' and warehouse='{}'  """.format(i.item_code,i.s_warehouse),as_dict=1)
            if get_bin:
                if get_bin[0]['qty']!=None:
                    actual_qty.append(get_bin[0]['qty'])


            #get draft stock
            get_se_draft=frappe.db.sql("""select sum(qty) as qty from `tabStock Entry Detail` where docstatus=0 and item_code='{}' and s_warehouse='{}' and parent in (select name from `tabStock Entry` where outgoing_stock_entry is null and docstatus=0) """.format(i.item_code,i.s_warehouse),as_dict=1)
            get_se_transit=frappe.db.sql("""select sum(qty) as qty from `tabStock Entry Detail` where docstatus=1 and item_code='{}' and s_warehouse='{}' and parent in (select name from `tabStock Entry`  where add_to_transit=1 and docstatus=1 and per_transferred<100)   """.format(i.item_code,i.s_warehouse),as_dict=1)
            if get_se_draft:
                if get_se_draft[0]['qty']!=None:
                    draft_stock.append(get_se_draft[0]['qty'])

            if get_se_transit:
                if get_se_transit[0]['qty']!=None:
                    transit_stock.append(get_se_transit[0]['qty'])

            #calculate qty
            new_qty=i.qty
            actua_stock=sum(actual_qty)
            #end transit button is showing
            #if doc.add_to_transit:
            transit_stock_total=sum(transit_stock)
            #if not doc.add_to_transit:
            total_stock_in_draft=sum(draft_stock)
            total_qty_transfered=transit_stock_total
            total_actual=abs(actua_stock-total_qty_transfered)
            if new_qty>total_actual:
                str="transit_stock_total:{},total_stock_in_draft:{},total_actual:{}".format(transit_stock_total,total_stock_in_draft,actua_stock)
                print(str,"str")
                frappe.throw("The quantity transfer for this item is in a pending stage.(कुछ  Stock Entry अभी Draft और transit Stage पर  हो सकती है ||पहले उनको Receive करना होगा ||)")
