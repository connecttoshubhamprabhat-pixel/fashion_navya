import frappe
from datetime import datetime # from python std library
from frappe.utils import add_to_date
from frappe import utils
from erpnext.stock.dashboard.item_dashboard import get_data
import json
from datetime import datetime # from python std library
from frappe.utils import add_to_date
from erpnext.stock.utils import get_latest_stock_qty

#Bank slip deposite
@frappe.whitelist()
def fetch_per_pending(from_time=None,to_time=None):
    condition="  "
    if from_time and to_time:
        from_time=str(from_time)
        to_time=str(to_time)
        condition +="and posting_date between '{}' and '{}' ".format(from_time,to_time)

    print(condition,"from")
    get_pe=frappe.db.sql(""" select name from `tabPayment Entry` where posting_date>"2022-12-30"  and payment_type="Internal Transfer" and docstatus=0  {} """.format(condition),as_dict=1)
    return get_pe



@frappe.whitelist()
def submit_all_pe(doc,method):
    if doc.deposited_slip:
        for i in doc.deposited_slip:
            pe=frappe.get_doc("Payment Entry",i.payment_entry)
            pe.submit()


@frappe.whitelist(allow_guest=True)
def calculate_total_amount(doc,method):
    amount=0
    for i in doc.deposited_slip:
        amount +=i.amount

    doc.set("total_amount",0.0)
    doc.set("total_amount",amount)


#only subcontracting
@frappe.whitelist(allow_guest=True)
def set_sell_item_po(doc,method):
    if not doc.get("__islocal") and doc.is_subcontracted:
        for i in doc.items:
            if i.fg_item:
                fgdoc=frappe.get_doc("Item",i.fg_item)
                # if fgdoc.parent_item!=None:
                #     i.db_set("fg_parent",i.parent_item, update_modified=False)


@frappe.whitelist()
def fetch_quation_sup(from_time=None,to_time=None,supplier=None):
    fetch_qo=frappe.db.sql(""" SELECT *  FROM `tabSupplier Quotation` WHERE NOT EXISTS(SELECT name from `tabPurchase Order Item` WHERE `tabPurchase Order Item`.supplier_quotation=`tabSupplier Quotation`.name)  and  transaction_date>"2023-05-05"  """,as_dict=1)
    return fetch_qo



@frappe.whitelist()
def make_task_temp(name=None):
    if not name:
        return

    today = datetime.now().strftime('%Y-%m-%d')
    after_3_days = add_to_date(datetime.now(), days=2, as_string=True)

    get_temp=frappe.db.sql(""" select DISTINCT name from `tabItem` where  has_variants=1 and project='{}'  """.format(name),as_dict=1)
    if len(get_temp)!=0:
        d={'doctype':"Task","project":name}
        for i in get_temp:
            tk=frappe.db.sql(""" select name from `tabTask` where subject='{}' """.format(i['name']),as_dict=1)
            if len(tk)==0:
                d['subject']=i['name']
                d['exp_start_date']=today
                d['exp_end_date']=after_3_days
                d['delivery_date']=after_3_days
                d['item']=i['name']
                tk_save=frappe.get_doc(d)
                tk_save.insert()
                frappe.db.commit()

    frappe.msgprint("Created")





@frappe.whitelist()
def fetch_amount_pim(doc,method):
	total=[0]
	if doc.references:
		for i in doc.references:
			if i.reference_doctype=="Supplier Quotation":
				sup=frappe.get_doc("Supplier Quotation",i.reference_name)
				i.set('amount',0.0)
				i.set('amount',sup.grand_total)
				total.append(sup.grand_total)

	if total:
		doc.set('total_amount',0.0)
		doc.set('total_amount',sum(total))


@frappe.whitelist()
def fetch_item_barcode(barcode=None):
	val=frappe.db.sql(""" select parent from `tabItem Barcode` where barcode='{}'    """.format(barcode),as_dict=1)
	if len(val)!=0:
		item=val[0]['parent']
		d=[]
		doc=frappe.get_doc("Item",item)
		if doc.item_group=="Sample":
			d.append(item)
			d.append("Sample")
		if doc.item_group=="Ready Stock":
			d.append(item)
			d.append("Ready Stock")
		if doc.item_group=="Customise":
			d.append(item)
			d.append("Customise")
		if len(d)==1:
			d.append("ss")
		if len(d)==2:
			return d


@frappe.whitelist()
def add_item_se(values=None,items=None):
    values=json.loads(values)
    items=json.loads(items)
    get_se=values.get("se")
    doc=frappe.get_doc("Stock Entry",get_se)
    target_W=doc.items[0].t_warehouse
    for i in items:
        item_doc=frappe.get_doc("Item",i.get("name"))
        data=get_data(item_code=item_doc.name)
        for j in data:
            if j['actual_qty']>0:
                row = doc.append("items", {})
                row.item_code=item_doc.name
                row.item_name=item_doc.item_name
                row.conversion_factor=1
                row.t_warehouse=target_W
                row.s_warehouse=j['warehouse']
                row.uom="Nos"
                row.qty=j['actual_qty']

    doc.save()
    frappe.msgprint("Updated")




@frappe.whitelist()
def filters_se_name(doctype, txt, searchfield, page_len, start, filters):
    return frappe.db.sql("""select name,owner from `tabStock Entry` where docstatus=0 and stock_entry_type='Material Transfer' ORDER BY modified DESC """)


@frappe.whitelist()
def filters_po_name(doctype, txt, searchfield, page_len, start, filters):
    return frappe.db.sql("""select name,owner from `tabPurchase Order` where docstatus=0 and is_subcontracted=0    ORDER BY modified DESC """)


@frappe.whitelist()
def filters_mr_name(doctype, txt, searchfield, page_len, start, filters):
    return frappe.db.sql("""select name,owner from `tabMaterial Request` where docstatus=0   ORDER BY modified DESC """)


#sales order after update
@frappe.whitelist()
def update_del_date_so(doc,method):
	for i in doc.items:
		ddate_so=str(i.delivery_date)
		nd = add_to_date(ddate_so, days=-3, as_string=True)
		get_mr=frappe.db.sql("""select DISTINCT  parent from  `tabMaterial Request Item` where item_code='{}' and sales_order='{}'  """.format(i.item_code,doc.name),as_dict=1)
		if get_mr:
			mr_list=[]
			for k in get_mr:
				if k['parent'] not in mr_list:
					frappe.db.sql("""update `tabMaterial Request` set schedule_date='{}' where name='{}'  """.format(nd,k['parent']))
					frappe.db.commit()
					mr_list.append(k['parent'])


		frappe.db.sql("""update `tabMaterial Request Item` set schedule_date='{}' where item_code='{}' and sales_order='{}'  """.format(nd,i.item_code,doc.name))
		frappe.db.commit()
		frappe.db.sql("""update `tabWork Order` set expected_delivery_date='{}' where sales_order='{}' and production_item='{}'  """.format(nd,doc.name,i.item_code))
		frappe.db.commit()




@frappe.whitelist()
def create_new_po_list(values=None,items=None):
    items=json.loads(items)
    values=json.loads(values)
    supplier=values.get("supplier")
    req=str(values.get("req"))
    if items and supplier:
        d={'doctype':"Purchase Order"}
        d['supplier']=supplier
        d['schedule_date']=req
        doc=frappe.get_doc(d)
        for i in items:
            item_doc=frappe.get_doc("Item",i.get("name"))
            row = doc.append("items", {})
            row.item_code=item_doc.name
            row.item_name=item_doc.item_name
            row.uom=item_doc.stock_uom
            row.schedule_date=req
            row.qty=1
        doc.insert(ignore_permissions=True)
        frappe.msgprint("Created")



@frappe.whitelist()
def create_new_mr_list(values=None,items=None):
    items=json.loads(items)
    values=json.loads(values)
    purpose=values.get("purpose")
    req=str(values.get("req"))
    if items and purpose:
        d={'doctype':"Material Request"}
        d['material_request_type']=purpose
        d['schedule_date']=req
        doc=frappe.get_doc(d)
        for i in items:
            item_doc=frappe.get_doc("Item",i.get("name"))
            row = doc.append("items", {})
            row.item_code=item_doc.name
            row.item_name=item_doc.item_name
            row.uom=item_doc.stock_uom
            row.schedule_date=req
            row.qty=1
        doc.insert(ignore_permissions=True)
        frappe.msgprint("Created")



@frappe.whitelist()
def add_item_po(values=None,items=None):
    values=json.loads(values)
    items=json.loads(items)
    get_po=values.get("po")
    doc=frappe.get_doc("Purchase Order",get_po)
    date=utils.today()
    if items:
        for i in items:
            item_doc=frappe.get_doc("Item",i.get("name"))
            row = doc.append("items", {})
            row.item_code=item_doc.name
            row.item_name=item_doc.item_name
            row.uom=item_doc.stock_uom
            row.qty=1

        doc.save()
        frappe.msgprint("Updated")


@frappe.whitelist()
def add_item_mr(values=None,items=None):
    values=json.loads(values)
    items=json.loads(items)
    get_mr=values.get("mr")
    doc=frappe.get_doc("Material Request",get_mr)
    req = datetime.now().date()
    if items:
        for i in items:
            item_doc=frappe.get_doc("Item",i.get("name"))
            row = doc.append("items", {})
            row.item_code=item_doc.name
            row.item_name=item_doc.item_name
            row.uom=item_doc.stock_uom
            row.qty=1
            row.schedule_date = req

        doc.save()
        frappe.msgprint("Updated")



@frappe.whitelist()
def make_stock_reconcil(items=None):
    items=json.loads(items)
    if items:
        d={'doctype':"Stock Reconciliation"}
        d['purpose']="Stock Reconciliation"
        doc=frappe.get_doc(d)
        inserts=[]
        for i in items:
            #frappe.msgprint("a")
            item=i.get("name")
            data=get_data(item_code=item)
            if data:
                for a in data:
                    if a['actual_qty']>0:
                        #frappe.msgprint("aw")
                        inserts.append("a")
                        #print(a,"aaaaa")
                        #print(item)
                        item_doc=frappe.get_doc("Item",item)
                        row = doc.append("items", {})
                        row.item_code=a['item_code']
                        #row.item_name=item_doc.item_name
                        row.qty=0
                        row.valuation_rate=a['valuation_rate']
                        row.current_qty=a['actual_qty']
                        row.warehouse=a['warehouse']

        if inserts:
            #print(doc.as_dict(),"aaaaaaaaaaaa")
            doc.insert(ignore_permissions=True)
            frappe.msgprint("Created")



@frappe.whitelist()
def update_stock_cron():
    get_items=frappe.db.sql("""select name from `tabItem` where item_group in ("Sample","Ready Stock","Customise") and variant_of is not null and project in ('PROJ-1564','PROJ-1587','Proj-1521','PROJ-1565','PROJ-1660','PROJ-1621','PROJ-1619','PROJ-1659','PROJ-1657','PROJ-1616')  """,as_dict=1)
    if get_items:
        for i in get_items:
            print(i['name'],"name")
            if frappe.db.exists("Item",i['name']):
                doc=frappe.get_doc("Item",i['name'])
                if doc.ignore_project==1:
                    doc.set("ignore_project",0)
                if doc.ignore_project==0:
                    doc.set("ignore_project",1)

                try:
                    doc.save(ignore_permissions=True)
                    frappe.db.commit()
                except:
                    continue


@frappe.whitelist()
def make_default_bom(doc,method):
    doc.set("is_active",1)
    doc.set("is_default",1)

@frappe.whitelist()
def make_mr_first_bom(doc,method):
    itemdoc=frappe.get_doc("Item",doc.item)
    if not itemdoc.variant_of:
        return
    check_mr_exists=frappe.db.sql("""select DISTINCT parent from `tabMaterial Request Item` where  item_code='{}' and  parent in (select name from `tabMaterial Request`  where docstatus=1 and custom_by_bom=1)  """.format(doc.item),as_dict=1)
    if len(check_mr_exists)!=0:
        return

    item_doc=frappe.get_doc("Item",doc.item)
    split=doc.item.split("-")
    qtys=[0]
    split_parent=item_doc.variant_of.split("-")[-1]
    if "RTW" in split:
        size=[]
        for i in item_doc.attributes:
             if i.attribute=="Size":
                size.append(i.attribute_value)
                break

        get_val=frappe.db.sql("""select capacity from `tabCapacity  Silhouette` where parent='{}' and parentfield="ready"  and sizes='{}'  """.format(split_parent,size[0]),as_dict=1)
        if get_val:
            capacity=get_val[0]['capacity']
            if capacity>0:
                 qtys.append(capacity)

        else:
             qtys.append(1)


    #make mr code
    today = datetime.now().strftime('%Y-%m-%d')
    after_3_days = add_to_date(datetime.now(), days=3, as_string=True)
    m={"doctype":"Material Request","material_request_type":"Manufacture"}
    m['schedule_date']=after_3_days
    m['custom_by_bom']=1
    m['project']=doc.project
    m['set_warehouse']="Navya Store Office - NAVYA"
    mr=frappe.get_doc(m)
    row = mr.append("items", {})
    row.item_code=doc.item
    row.qty=sum(qtys) or 1
    row.warehouse="Navya Store Office - NAVYA"
    row.uom="Nos"
    row.schedule_date=after_3_days
    mr.insert()
    mr.submit()
    frappe.msgprint("MR is created")




@frappe.whitelist()
def update_price_item(doc,method):
    item_doc=frappe.get_doc("Item",doc.item_code)
    if item_doc.ignore_project==1:
        item_doc.set("ignore_project",0)
    if item_doc.ignore_project==0:
        item_doc.set("ignore_project",1)
    #item_doc.save(ignore_permissions=True)


@frappe.whitelist()
def update_price_item_bom(doc,method):
    item_doc=frappe.get_doc("Item",doc.item)
    if item_doc.ignore_project==1:
        item_doc.set("ignore_project",0)
    if item_doc.ignore_project==0:
        item_doc.set("ignore_project",1)
    item_doc.save(ignore_permissions=True)


@frappe.whitelist()
def update_is_whatsapp():
    get_contact=frappe.db.sql("""select parent from `tabContact Phone` where phone is not null and is_whatsapp_number=0 """,as_dict=1)
    if get_contact:
        for i in get_contact:
            print(i,"qqqqqqqqqqqqqqq")
            contact=frappe.get_doc("Contact",i['parent'])
            contact.set("whatsapp_no",contact.phone_nos[0].phone)
            contact.set("activate_whatsapp",1)
            try:
                contact.save()
                frappe.db.commit()
            except:
                continue



@frappe.whitelist()
def make_po_orders_project(items=None,values=None,project=None):
    items=json.loads(items)
    values=json.loads(values)
    sitem=values.get("sitem")
    supplier=values.get("supplier")
    po_type=values.get("po_type")
    sqty=values.get("sqty")
    fg_qty=values.get("fg_qty")
    rqdate=str(values.get("rqdate"))
    if items:
        d={"doctype":"Purchase Order","supplier":supplier,"is_subcontracted":1}
        d['schedule_date']=rqdate
        d['project']=project
        attributes_list=["DP","BP","HE","FBP"]
        #supplier_dict={"Samsudeen Aakil Khan":"BPK","PRINTTECH":"DPK",""}
        doc=frappe.get_doc(d)
        yes_items=[]
        for i in items:
            is_items=[]
            main_item=i
            attributes_kit=["k"]
            split_parent=i.split("-")
            for j in attributes_list:
                if j in split_parent:
                    attributes_kit.append(j)
            for kit in attributes_kit:
                fg_yes=[]
                row=doc.append("items", {})
                row.item_code=sitem
                row.qty=sqty
                row.fg_item_qty=fg_qty
                row.fg_parent=i
                print(i,'i')
                if kit=="k":
                    if frappe.db.exists("Item",main_item+"-"+"k"):
                        k1=main_item+"-"+"k"
                        row.fg_item=k1
                        make_check_subcontract(name=k1)
                        fg_yes.append("987")
                        print(k1,'k1')
                    else:
                        frappe.msgprint("Main Kit Item is missing for {}".format(i))
                if kit=="DP":
                    if frappe.db.exists("Item",main_item+"-"+"DPK"):
                        k2=main_item+"-"+"DPK"
                        row.fg_item=k2
                        make_check_subcontract(name=k2)
                        print(k2,"k2")
                        fg_yes.append("2")
                    else:
                        frappe.msgprint("DPK Kit Item is missing for {}".format(i))
                if kit=="BP":
                    if frappe.db.exists("Item",main_item+"-"+"BPK"):
                        k3=main_item+"-"+"BPK"
                        row.fg_item=k3
                        make_check_subcontract(name=k3)
                        print(k3,"k3")
                        fg_yes.append("9")

                    else:
                        frappe.msgprint("BPK Kit Item is missing for {}".format(i))

                if kit=="HE":
                    if frappe.db.exists("Item",main_item+"-"+"HEK"):
                        k4=main_item+"-"+"HEK"
                        row.fg_item=main_item+"-"+"HEK"
                        make_check_subcontract(name=k4)
                        print(k4,"k4")
                        fg_yes.append("a")
                    else:
                        frappe.msgprint("Main Kit Item is missing for {}".format(i))

                if fg_yes:
                     yes_items.append("aa")
                     row.item_code=sitem
        if yes_items:
             doc.insert()
             print(doc.as_dict(),"dict")
             frappe.msgprint("Created")





@frappe.whitelist()
def check_duplciate(doc,method):
	if doc.uoms:
		check=[]
		duplicated=[]
		for i in doc.uoms:
			if i.uom not in  check:
				check.append(i.uom)
			else:
				duplicated.append("aa")

		if duplicated and check:
			for j in check:
				row = doc.append("uoms", {})
				row.uom=j
	if doc.item_defaults:
		check=[]
		duplicated=[]
		for i in doc.item_defaults:
			if i.company not in  check:
				check.append(i.company)
			else:
				duplicated.append("aa")

		if duplicated and check:
			for j in check:
				row = doc.append("item_defaults", {})
				row.uom=j

@frappe.whitelist()
def make_check_subcontract(name=None):
    if not name:
         return

    doc=frappe.get_doc("Item",name)
    split=doc.name.split("-")
    if doc.is_sub_contracted_item==0 and "BPK" not in split:
        doc.set("is_sub_contracted_item",1)
        doc.save()



@frappe.whitelist()
def make_print_tag(items=None):
    items=json.loads(items)
    if items:
        d={"doctype":"Item Discount Print Tag"}
        doc=frappe.get_doc(d)
        for i in items:
            row = doc.append("items", {})
            row.item_code=i.get("name")

        doc.save()
        frappe.msgprint("created")

@frappe.whitelist()
def make_print_data_asset(items=None):
    items=json.loads(items)
    if items:
        d={"doctype":"Catalogue"}
        doc=frappe.get_doc(d)
        images=[]
        for i in items:
            itemdoc=frappe.get_doc("Asset",i.get("name"))
            if itemdoc.image not in images:
                row = doc.append("items", {})
                row.item_code=i.get("name")
                row.image = itemdoc.image
                images.append(itemdoc.image)

        doc.save()
        frappe.msgprint("created")

# @frappe.whitelist()
# def make_print_cata(items=None):
#     items=json.loads(items)
#     if items:
#         d={"doctype":"Catalogue"}
#         doc=frappe.get_doc(d)
#         images=[]
#         for i in items:
#             itemdoc=frappe.get_doc("Item",i.get("name"))
#             if itemdoc.image not in images:
#                 row = doc.append("items", {})
#                 row.item_code=i.get("name")
#                 images.append(itemdoc.image)

#         doc.subject = 'Automated'
#         doc.save()
#         frappe.msgprint("created")
@frappe.whitelist()
def make_print_cata(items=None):
    items = json.loads(items)
    # print("items----------------->",items)
    if items:
        d = {"doctype": "Catalogue"}
        doc = frappe.get_doc(d)
        images = []

        for i in items:
            itemdoc = frappe.get_doc("Item", i.get("name"))

            if itemdoc.image not in images:
                row = doc.append("items", {})
                row.item_code = i.get("name")
                images.append(itemdoc.image)

                bins = frappe.get_all("Bin", filters={"item_code": i.get("name"), "actual_qty": [">", 0]},
                                      fields=["warehouse", "actual_qty"])

                bin_text = ", ".join([f"{bin['warehouse']}: {bin['actual_qty']}" for bin in bins])

                row.bins = bin_text

        # doc.subject = 'Automated'
        doc.save()
        frappe.msgprint("Catalogue created successfully")

@frappe.whitelist()
def fetch_net_stock(doc,method):
	if doc.warehouse:
		w=frappe.get_doc("Warehouse",doc.warehouse)
		warehouse_list=[]


		if w.is_group:
			get_n=frappe.db.sql(""" select name from `tabWarehouse`   where parent_warehouse='{}' and   disabled=0 """.format(doc.warehouse),as_dict=1)
			if len(get_n)!=0:
				for w in get_n:
					warehouse_list.append(w['name'])



		else:
			warehouse_list.append(w.name)



		if doc.items:
			for i in doc.items:
				i.set("net_stock",0)
				i.set("available_in",None)
				net_stock=[0]
				sizes=" "
				sdic={}
				get_items=frappe.db.sql(""" select DISTINCT name from `tabItem` where  image='{}'   """.format(i.image),as_dict=1)
				if len(get_items)!=0:
					for j in get_items:
						item=frappe.get_doc("Item",j['name'])
						for a in item.attributes:
							if a.attribute=="Size":
								get_abr=frappe.db.sql("""select abbr from `tabItem Attribute Value` where attribute_value='{}'  """.format(a.attribute_value),as_dict=1)
								if get_abr:
									if get_abr[0]['abbr'] in sdic:
										sdic[get_abr[0]['abbr']]+=1
									else:
										sdic[get_abr[0]['abbr']]=1

						for w in warehouse_list:
							qty=get_latest_stock_qty(item_code=j['name'],warehouse=w)
							if qty!=None:
								net_stock.append(qty)

				for key,val in sdic.items():
					sizes +="{}{},".format(key,val)

				i.set("available_in",sizes)
				i.set("net_stock",sum(net_stock))




@frappe.whitelist()
def update_putway_rule(doc,method):
    if doc.outgoing_stock_entry and doc.custom_ignore_putway==0:
        se=frappe.get_doc("Stock Entry",doc.outgoing_stock_entry)
        if se.custom_destination:
            doc.set("apply_putaway_rule",1)


@frappe.whitelist()
def set_read_flilter_logs(doc,method):
	if doc.read:
		doc.set("custom_log_check","Read")



@frappe.whitelist()
def set_warehouse_wos_1(doc,method):
    if doc.custom_skip_warehouse:
         return
    doc.set("wip_warehouse","Sampling Unit - NAVYA")
    doc.set("fg_warehouse","Navya Store Office - NAVYA")
    itemdoc=frappe.get_doc("Item",doc.production_item)
    if doc.sales_order:
        return

    if not itemdoc.variant_of:
        split_name=itemdoc.name.split("-")
        get_parent_name=split_name[:-1]
        if frappe.db.exists("Item",get_parent_name) and doc.production_plan:
            get_wo_parent=frappe.db.sql("""select name from `tabWork Order` where docstatus<2 and production_plan='{}' and production_item='{}'  """.format(doc.production_plan,get_parent_name),as_dict=1)
            if len(get_wo_parent)!=0:
                wo_parent_doc=frappe.get_doc("Work Order",get_wo_parent[0]['name'])
                doc.set("wip_warehouse",wo_parent_doc.wip_warehouse)
                doc.set("fg_warehouse",wo_parent_doc.fg_warehouse)
                return
            else:
                doc.set("wip_warehouse","Sampling Unit - NAVYA")
                doc.set("fg_warehouse","Navya Store Office - NAVYA")
                return


    is_so=[]
    if doc.production_plan:
        pp=frappe.get_doc("Production Plan",doc.production_plan)
        if pp.custom_production_plan_type in ["Sales Order"]:
            is_so.append("a")



    split_item=doc.production_item.split("-")
    if not is_so and "BP" in  split_item and "RTW" in split_item and doc.custom_skip_warehouse==0:
        doc.set("wip_warehouse","Libberheri Work In Progress - NAVYA")
        doc.set("fg_warehouse","Libberhedi finished Products - NAVYA")
        if not itemdoc.variant_of:
            doc.set("wip_warehouse","Semi Finished Libberhedi - NAVYA")
            doc.set("fg_warehouse","Libberhedi finished Products - NAVYA")

        if doc.operations:
             for i in doc.operations:
                  i.set("workstation","Libberheri Unit")
    else:
        if not itemdoc.variant_of:
            doc.set("wip_warehouse","Semi finished Sampling Unit - NAVYA")
            doc.set("fg_warehouse","Navya Store Office - NAVYA")





@frappe.whitelist()
def make_pattern_copy(values=None,newcode=None):
    values=json.loads(values)
    name=values.get("item_code")
    get_ptt=frappe.db.sql("""select name from `tabPattern` where item_code='{}' and docstatus=1  """.format(name),as_dict=1)
    if len(get_ptt)!=0:
         for i in get_ptt:
            old_ptt=frappe.get_doc("Pattern",i['name'])
            new_patt=frappe.copy_doc(old_ptt)
            new_patt.set("item_code",newcode)
            new_patt.set("docstatus",0)
            new_patt.set("workflow_state","Draft")
            try:
                 new_patt.insert()

            except:
                 pass

            #new_patt.submit()
            frappe.msgprint("created")



@frappe.whitelist()
def set_branch_jc(doc,method):
    if doc.work_order:
        wo=frappe.get_doc("Work Order",doc.work_order)
        if wo.fg_warehouse in ['Libberhedi finished Products - NAVYA']:
             doc.set("custom_branch","Libberhedi")

        if wo.fg_warehouse in ['Navya Store Office - NAVYA','Courier Station - NAVYA']:
             doc.set("custom_branch","Sainik Farms")





@frappe.whitelist()
def add_item_to_wocom(items=None):
    items=json.loads(items)
    if items:
        d={"doctype":"WooCommerce Product"}
        for item in items:
             doc=frappe.get_doc("Item",item)
             d={"doctype":"WooCommerce Product"}
             d['woocommerce_name']=doc.item_name
             d['sku']=doc.name

        doc.save()
        frappe.msgprint("created")





@frappe.whitelist()
def set_warehouse_wo(doc, method):
    if doc.custom_skip_warehouse:
        return

    default_wip_warehouse = "Sampling Unit - NAVYA"
    default_fg_warehouse = "Navya Store Office - NAVYA"

    doc.set("wip_warehouse", default_wip_warehouse)
    doc.set("fg_warehouse", default_fg_warehouse)

    itemdoc = frappe.get_doc("Item", doc.production_item)

    if doc.sales_order:
        return

    if not itemdoc.variant_of:
        split_name = itemdoc.name.split("-")
        get_parent_name = "-".join(split_name[:-1])

        if frappe.db.exists("Item", get_parent_name) and doc.production_plan:
            get_wo_parent = frappe.db.sql("""
                select name from `tabWork Order`
                where docstatus < 2
                  and production_plan = %s
                  and production_item = %s
            """, (doc.production_plan, get_parent_name), as_dict=1)

            if get_wo_parent:
                wo_parent_doc = frappe.get_doc("Work Order", get_wo_parent[0]['name'])
                doc.set("wip_warehouse", wo_parent_doc.wip_warehouse)
                doc.set("fg_warehouse", wo_parent_doc.fg_warehouse)
                return
            else:
                doc.set("wip_warehouse", default_wip_warehouse)
                doc.set("fg_warehouse", default_fg_warehouse)
                return

    is_so = []
    if doc.production_plan:
        pp = frappe.get_doc("Production Plan", doc.production_plan)
        if pp.custom_production_plan_type == "Sales Order":
            is_so.append("a")

    split_item = doc.production_item.split("-")
    if not is_so and "BP" in split_item and "RTW" in split_item and not doc.custom_skip_warehouse:
        doc.set("wip_warehouse", "Libberheri Work In Progress - NAVYA")
        doc.set("fg_warehouse", "Libberhedi Finished Products - NAVYA")

        if not itemdoc.variant_of:
            doc.set("wip_warehouse", "Semi Finished Libberhedi - NAVYA")
            doc.set("fg_warehouse", "Libberhedi Finished Products - NAVYA")

        if doc.operations:
            for operation in doc.operations:
                operation.set("workstation", "Libberheri Unit")

    else:
        if not itemdoc.variant_of:
            doc.set("wip_warehouse", "Semi Finished Sampling Unit - NAVYA")
            doc.set("fg_warehouse", default_fg_warehouse)






@frappe.whitelist()
def add_to_catalogue(items, catalogue):
    import json

    if isinstance(items, str):
        items = json.loads(items)

    if not items or not catalogue:
        frappe.throw(_("Items or Catalogue cannot be empty."))

    if frappe.db.exists("Catalogue", {"name": catalogue}):
        cat_doc = frappe.get_doc("Catalogue", catalogue)

        for item_code in items:
            cat_doc.append("items", {"item_code": item_code})

        cat_doc.save(ignore_permissions=True)

        frappe.db.commit()

        frappe.msgprint(_("Items successfully added to catalogue {0}").format(catalogue))
    else:
        frappe.throw(_("Catalogue {0} does not exist.").format(catalogue))

