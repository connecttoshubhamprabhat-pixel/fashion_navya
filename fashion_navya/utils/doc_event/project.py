import frappe
import json
from fashion_navya.utils.overides.mr import *

@frappe.whitelist(allow_guest=True)
def calculated_qty_project(doc,method):
    smpl=[0]
    rtw=[0]
    smpl_wo_qty_total=[0]
    smpl_mn_qty_total=[0]
    rtw_wo_qty_total=[0]
    rtw_mn_qty_total=[0]
    no_started_smpl=[0]
    no_started_rtw=[0]


    if doc.custom_sample_pending:
        for i in doc.custom_sample_pending:
            smpl.append(i.mnqty)
            smpl_wo_qty_total.append(i.wqty)
            smpl_mn_qty_total.append(i.mn_qtyw)
            nssmpl=get_not_started_wo_1(i.item)
            no_started_smpl.append(nssmpl)


            
    if doc.custom_rtw_pending:
        for i in doc.custom_rtw_pending:
            rtw.append(i.mnqty)
            rtw_wo_qty_total.append(i.wqty)
            rtw_mn_qty_total.append(i.mn_qtyw)
            nsrtw=get_not_started_wo_1(i.item)
            no_started_rtw.append(nsrtw)
    

    doc.set("custom_pqtynsmpl",0)
    doc.set("custom_rtwnwo",0)
    doc.set("custom_pqtynsmpl",sum(no_started_smpl))
    doc.set("custom_rtwnwo",sum(no_started_rtw))
    
    

    
    doc.set("custom_wo_qty_smpl",0)
    doc.set("custom_mnqty_smpl",0)
    doc.set("custom_wo_qty_smpl",sum(smpl_wo_qty_total))
    doc.set("custom_mnqty_smpl",sum(smpl_mn_qty_total))
    
    doc.set("custom_rtw_wo_qty",0)
    doc.set("custom_rtw_manufactured",0)
    doc.set("custom_rtw_wo_qty",sum(rtw_wo_qty_total))
    doc.set("custom_rtw_manufactured",sum(rtw_mn_qty_total))
    
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
            if len(se)!=0 and len(get_wo)!=0:
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


@frappe.whitelist(allow_guest=True)
def get_not_started_wo_1(item=None):
    get_wo=frappe.db.sql("""select sum(qty) as qty from `tabWork Order` where docstatus=1 and status='Not Started' and production_item='{}'  """.format(item),as_dict=1)
    if len(get_wo)!=0:
        if get_wo[0]['qty']!=None:
            return get_wo[0]['qty']
        else:
            return 0
    else:
        return 0




@frappe.whitelist(allow_guest=True)
def get_not_started_wo(values=None):
    values=json.loads(values)
    project=values.get("project")
    lists_mr=[]
    get_mr=frappe.db.sql("""select name from `tabMaterial Request`  where  docstatus=1 and  status!="Stopped"  and material_request_type="Manufacture" and per_ordered<90  and project='{}'  """.format(project),as_dict=1)
    if len(get_mr)!=0:
        for i in get_mr:
            d={}
            d['mr']=i['name']
            lists_mr.append(d)
    if lists_mr:
        return lists_mr
    else:
        return []


@frappe.whitelist(allow_guest=True)
def get_not_started_pro(project=None):
    lists_mr=[]
    get_mr=frappe.db.sql("""select name from `tabMaterial Request`  where  docstatus=1 and  status!="Stopped"  and material_request_type="Manufacture" and per_ordered<90  and project='{}'  """.format(project),as_dict=1)
    if len(get_mr)!=0:
        for i in get_mr:
            lists_mr.append(i['name'])
    
    if lists_mr:
        d={"doctype":"Production Plan","get_items_from":"Material Request"}
        d['project']=project
        doc=frappe.get_doc(d)
        for j in lists_mr:
            row = doc.append("material_requests", {})
            row.material_request=j
            
        get_mr_items_custom(doc)
        doc.insert()
        frappe.msgprint("Created")
    else:
        frappe.msgprint("Make MR fisrt")
    



@frappe.whitelist(allow_guest=True)
def get_not_started_pro_bulk(items=None):
    items=json.loads(items)
    if items:
        for p in items:
            project=p
            lists_mr=[]
            get_mr=frappe.db.sql("""select name from `tabMaterial Request`  where  docstatus=1 and  status!="Stopped"  and material_request_type="Manufacture" and per_ordered<90  and project='{}'  """.format(project),as_dict=1)
            if len(get_mr)!=0:
                for i in get_mr:
                    lists_mr.append(i['name'])
            
            if lists_mr:
                d={"doctype":"Production Plan","get_items_from":"Material Request","custom_automated":1}
                d['project']=project
                doc=frappe.get_doc(d)
                for j in lists_mr:
                    row = doc.append("material_requests", {})
                    row.material_request=j
                    
                get_mr_items_custom(doc)
                get_sub_assembly_items(doc, manufacturing_type=None)
                doc.insert()
                doc.set("for_warehouse","Sampling Unit - NAVYA")
                warehouses_mr=["Sampling Unit - NAVYA"]
                warehouse_list_mr=[{"warehouse":"Sampling Unit - NAVYA"}]
                dump_Warehoues=json.dumps(warehouse_list_mr)
                for w in warehouses_mr:
                    warehouse_list_mr=[{"warehouse":w}]
                    dump_Warehoues=json.dumps(warehouse_list_mr)
                    mr_items=get_items_for_material_requests_custom(doc,warehouses=dump_Warehoues,get_parent_warehouse_data=None)
                    if mr_items:
                        for d in mr_items:
                            print(d.get("item_code"))
                            item_doc=frappe.get_doc("Item",d.get("item_code"))
                            if item_doc.disabled==1:
                                continue
                            
                            doc.append(
                                        "mr_items",
                                        {
                                                "item_code":d.get("item_code"),
                                            "item_name":d.get("item_name"),
                                            "description":d.get("description"),
                                            "stock_uom":d.get("stock_uom"),
                                            "warehouse":d.get("warehouse"),
                                            "required_bom_qty":d.get("required_bom_qty"),
                                            "projected_qty":d.get("projected_qty"),
                                            "actual_qty":d.get("actual_qty"),
                                            "ordered_qty":d.get("ordered_qty"),
                                            "planned_qty":d.get("planned_qty"),
                                            "reserved_qty_for_production":d.get("reserved_qty_for_production"),
                                            "safety_stock":d.get("safety_stock"),
                                            "quantity":d.get("quantity"),
                                            "material_request_type":d.get("material_request_type"),


                                            },
                                        )
                            
                            
                doc.submit()
                make_material_request_custom(doc)
                make_work_order(doc)
                frappe.db.commit()
                frappe.msgprint("Created")
                
            else:
                continue




#automated this project
@frappe.whitelist(allow_guest=True)
def get_not_started_pro_bulk_auto():
    projects=frappe.db.sql("""select DISTINCT project from `tabMaterial Request` where docstatus=1 and material_request_type='Manufacture'  """,as_dict=1)
    items=[]
    for a in projects:
        items.append(a['project'])
        
    items=list(set(items))
    if items:
        for p in items:
            project=p
            lists_mr=[]
            get_mr=frappe.db.sql("""select name from `tabMaterial Request`  where  docstatus=1 and  status!="Stopped"  and material_request_type="Manufacture" and per_ordered<90  and project='{}'  """.format(project),as_dict=1)
            if len(get_mr)!=0:
                for i in get_mr:
                    lists_mr.append(i['name'])
            
            if lists_mr:
                d={"doctype":"Production Plan","get_items_from":"Material Request","custom_automated":1}
                d['project']=project
                doc=frappe.get_doc(d)
                for j in lists_mr:
                    row = doc.append("material_requests", {})
                    row.material_request=j
                    
                get_mr_items_custom(doc)
                get_sub_assembly_items(doc, manufacturing_type=None)
                if len(doc.po_items)==0:
                    continue
                doc.insert()
                doc.set("for_warehouse","Sampling Unit - NAVYA")
                warehouses_mr=["Sampling Unit - NAVYA"]
                warehouse_list_mr=[{"warehouse":"Sampling Unit - NAVYA"}]
                dump_Warehoues=json.dumps(warehouse_list_mr)
                for w in warehouses_mr:
                    warehouse_list_mr=[{"warehouse":w}]
                    dump_Warehoues=json.dumps(warehouse_list_mr)
                    mr_items=get_items_for_material_requests_custom(doc,warehouses=dump_Warehoues,get_parent_warehouse_data=None)
                    if mr_items:
                        for d in mr_items:
                            print(d.get("item_code"))
                            item_doc=frappe.get_doc("Item",d.get("item_code"))
                            if item_doc.disabled==1:
                                continue
                            
                            doc.append(
                                        "mr_items",
                                        {
                                                "item_code":d.get("item_code"),
                                            "item_name":d.get("item_name"),
                                            "description":d.get("description"),
                                            "stock_uom":d.get("stock_uom"),
                                            "warehouse":d.get("warehouse"),
                                            "required_bom_qty":d.get("required_bom_qty"),
                                            "projected_qty":d.get("projected_qty"),
                                            "actual_qty":d.get("actual_qty"),
                                            "ordered_qty":d.get("ordered_qty"),
                                            "planned_qty":d.get("planned_qty"),
                                            "reserved_qty_for_production":d.get("reserved_qty_for_production"),
                                            "safety_stock":d.get("safety_stock"),
                                            "quantity":d.get("quantity"),
                                            "material_request_type":d.get("material_request_type"),


                                            },
                                        )
                            
                            
                doc.submit()
                make_material_request_custom(doc)
                make_work_order(doc)
                frappe.db.commit()
                #frappe.msgprint("Created")
                
            else:
                continue






