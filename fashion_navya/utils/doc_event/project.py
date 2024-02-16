import frappe

@frappe.whitelist(allow_guest=True)
def calculated_qty_project(doc,method):
    smpl=[0]
    rtw=[0]
    if doc.custom_sample_pending:
        for i in doc.custom_sample_pending:
            smpl.append(i.mnqty)
            
    if doc.custom_rtw_pending:
        for i in doc.custom_rtw_pending:
            rtw.append(i.mnqty)
            
    doc.set("custom_smpl_qty",0)
    doc.set("custom_rtw_qty",0)
    doc.set("custom_smpl_qty",sum(smpl))
    doc.set("custom_rtw_qty",sum(rtw))
    net_smpl=[0]
    net_rtw=[0]
    
    if doc.project_attribute:
        for i in doc.project_attribute:
            if i.net_stock_value:
                stock_n=i.net_stock_value
                net_smpl.append(int(stock_n))
                
    if doc.item_ready:
        for i in doc.item_ready:
            if i.net_stock_value:
                stock_n1=i.net_stock_value
                net_rtw.append(int(stock_n1))
                
    doc.set("custom_smpl_net_qty",0)
    doc.set("custom_rtw_net_qty",0)
    doc.set("custom_smpl_net_qty",sum(net_smpl))
    doc.set("custom_rtw_net_qty",sum(net_rtw))

    #data collect
    total_net_stock=doc.custom_smpl_net_qty+doc.custom_rtw_net_qty
    total_p_wo_qty=int(doc.custom_smpl_qty)+int(doc.custom_rtw_qty)
    string_name="SMPL NS:{},RTW NS:{},SMPL P {},RTW P {}".format(doc.custom_smpl_net_qty,doc.custom_rtw_net_qty,int(doc.custom_smpl_qty),int(doc.custom_rtw_qty))
    doc.set("custom_titles",string_name)
    
    
    
@frappe.whitelist(allow_guest=True)
def pending_qty_kit(doc,method):
    vitem=frappe.db.sql("""select name from `tabItem` where project='{}' and variant_of is not null     """.format(doc.name),as_dict=1)
    get_bpk=frappe.db.sql("""select name from `tabItem` where project='{}' and  name like  '%-BPK'     """.format(doc.name),as_dict=1)
    get_kit=frappe.db.sql("""select name from `tabItem` where project='{}' and  name like  '%-k'     """.format(doc.name),as_dict=1)
    get_hek=frappe.db.sql("""select name from `tabItem` where project='{}' and name like  '%-HEK'     """.format(doc.name),as_dict=1)
    get_dpk=frappe.db.sql("""select name from `tabItem` where project='{}' and name like  '%-DPK'     """.format(doc.name),as_dict=1)
    if get_bpk:
        doc.custom_bpk_pending=[]
        for i in get_bpk:
            item=i['name']
            qty=[0]
            pqty=[0]
            get_wo=frappe.db.sql(""" select qty,produced_qty from `tabWork Order` where docstatus=1 and qty!=produced_qty and status in  ('In Process','Not Started') and production_item='{}' """.format(item),as_dict=1)
            if get_wo:
                for j in get_wo:
                    qty.append(j['qty'])
                    pqty.append(j['produced_qty'])
            diff=sum(qty)-sum(pqty)
            if diff:
                row = doc.append("custom_bpk_pending", {})
                row.item=item
                row.wqty=sum(qty)
                row.mn_qtyw=sum(pqty)
                row.mnqty=diff



    
    if get_hek:
        doc.custom_hek_pending=[]
        for i in get_hek:
            item=i['name']
            qty=[0]
            pqty=[0]
            get_wo=frappe.db.sql(""" select qty,produced_qty from `tabWork Order` where docstatus=1 and qty!=produced_qty and status in  ('In Process','Not Started') and production_item='{}'  """.format(item),as_dict=1)
            if get_wo:
                for j in get_wo:
                    qty.append(j['qty'])
                    pqty.append(j['produced_qty'])
            diff=sum(qty)-sum(pqty)
            if diff:
                row = doc.append("custom_hek_pending", {})
                row.item=item
                row.wqty=sum(qty)
                row.mn_qtyw=sum(pqty)
                row.mnqty=diff

    
    if get_dpk:
        doc.custom_dpk_pending=[]
        for i in get_dpk:
            item=i['name']
            qty=[0]
            pqty=[0]
            get_wo=frappe.db.sql(""" select qty,produced_qty from `tabWork Order` where docstatus=1 and qty!=produced_qty and status in  ('In Process','Not Started') and production_item='{}'  """.format(item),as_dict=1)
            if get_wo:
                for j in get_wo:
                    qty.append(j['qty'])
                    pqty.append(j['produced_qty'])
            diff=sum(qty)-sum(pqty)
            if diff:
                row = doc.append("custom_dpk_pending", {})
                row.item=item
                row.wqty=sum(qty)
                row.mn_qtyw=sum(pqty)
                row.mnqty=diff
    

    if get_kit:
        doc.custom_mkit=[]
        for i in get_kit:
            item=i['name']
            qty=[0]
            pqty=[0]
            get_wo=frappe.db.sql(""" select qty,produced_qty from `tabWork Order` where docstatus=1 and qty!=produced_qty and status in  ('In Process','Not Started') and production_item='{}'  """.format(item),as_dict=1)
            if get_wo:
                for j in get_wo:
                    qty.append(j['qty'])
                    pqty.append(j['produced_qty'])
            diff=sum(qty)-sum(pqty)
            if diff:
                row = doc.append("custom_mkit", {})
                row.item=item
                row.wqty=sum(qty)
                row.mn_qtyw=sum(pqty)
                row.mnqty=diff

    if vitem:
        doc.custom_wop=[]
        for v in vitem:
            item=v['name']
            qty=[0]
            pqty=[0]
            net=[0]
            se=frappe.db.sql(""" select name from `tabStock Entry Detail` where docstatus=1 and item_code='{}'  and  is_finished_item=1  """.format(item),as_dict=1)
            size=frappe.db.sql(""" select attribute_value from `tabItem Variant Attribute` where attribute="Size" and parentfield="attributes" and parent='{}' """.format(item),as_dict=1)
            net_stock=frappe.db.sql(""" select sum(actual_qty) as qty from `tabBin` where item_code='{}'  and actual_qty>0  """.format(item),as_dict=1)
            if net_stock:
                if net_stock[0]['qty']!=None:
                    net.append(net_stock[0]['qty'])

            get_wo=frappe.db.sql(""" select qty,produced_qty from `tabWork Order` where docstatus=1 and  production_item='{}'  """.format(item),as_dict=1)
            if get_wo:
                for j in get_wo:
                    qty.append(j['qty'])
                    pqty.append(j['produced_qty'])
                    
            diff=sum(qty)-sum(pqty)
            row = doc.append("custom_wop", {})
            row.item=item
            row.wqty=sum(qty)
            row.mn_qtyw=sum(pqty)
            row.mnqty=diff
            row.net_stock=sum(net)
            if size:
                row.size=size[0]['attribute_value']
            if len(se)!=0:
                row.manufactured=1
