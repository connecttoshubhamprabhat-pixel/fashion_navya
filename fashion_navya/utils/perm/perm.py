import frappe


#check for transfer entry
@frappe.whitelist()
def check_stock_warehouse_source(doc,method):
    skip_user=['Administrator','pawasthy11@gmail.com','amita@navya.biz',"erpsupport@uttamenergy.com"]
    if doc.rfse=="Dry clean":
        roles=frappe.get_roles(frappe.session.user)
        if "Sales Executive" in roles:
            return
    if doc.doctype=="Stock Entry" and not doc.outgoing_stock_entry and not doc.pick_list:
        user=frappe.session.user
        source_warehouse=[]
        if doc.stock_entry_type=="Material Transfer" and user not in skip_user:
            get_perm_file=frappe.db.sql(""" select name from `tabPermitted Files` where document_name="Stock Entry"  and docstatus <2 """,as_dict=1)
            if len(get_perm_file)!=0:
                fdoc=frappe.get_doc("Permitted Files",get_perm_file[0]['name'])
                if fdoc.wlocation:
                    for w in fdoc.wlocation:
                        if w.user==user:
                            source_warehouse.append(w.warehouse)

                for i in doc.items:
                    if i.s_warehouse not in source_warehouse:
                        msg="Sorry Source Warehouse is wrong ,Row {}".format(i.idx)
                        frappe.throw(msg)


@frappe.whitelist()
def check_stock_warehouse_target(doc,method):
    if doc.rfse=="Dry clean":
        roles=frappe.get_roles(frappe.session.user)
        if "Sales Manager" in roles and doc.custom_destination=="Navya Store Office - NAVYA":
            return
    skip_user=['Administrator','pawasthy11@gmail.com','amita@navya.biz',"erpsupport@uttamenergy.com"]
    if doc.doctype=="Stock Entry" and not doc.outgoing_stock_entry:
        user=frappe.session.user
        target_warehouse=[]
        if doc.stock_entry_type=="Material Transfer" and user not in skip_user:
            get_perm_file=frappe.db.sql(""" select name from `tabPermitted Files` where document_name="Stock Entry"  and docstatus <2 """,as_dict=1)
            if len(get_perm_file)!=0:
                fdoc=frappe.get_doc("Permitted Files",get_perm_file[0]['name'])
                if fdoc.wlocation:
                    for w in fdoc.wlocation:
                        if w.user==user:
                            target_warehouse.append(w.warehouse)

            for i in doc.items:
                if i.t_warehouse not in target_warehouse:
                    msg="Sorry target Warehouse is wrong ,Row {}".format(i.idx)
                    frappe.throw(msg)





