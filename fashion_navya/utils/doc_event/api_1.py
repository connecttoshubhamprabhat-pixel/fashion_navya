import frappe
from datetime import datetime # from python std library
from frappe.utils import add_to_date
from frappe import utils
from erpnext.stock.dashboard.item_dashboard import get_data
import json
from datetime import datetime # from python std library
from frappe.utils import add_to_date

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
    get_items=frappe.db.sql("""select name from `tabItem` where item_group in ("Sample","Ready Stock") and variant_of is not null  """,as_dict=1)
    if get_items:
        for i in get_items:
            if frappe.db.exists("Item",i['name']):
                doc=frappe.get_doc("Item",i['name'])
                if doc.ignore_project==1:
                    doc.set("ignore_project",0)
                if doc.ignore_project==0:
                    doc.set("ignore_project",1)

                doc.save(ignore_permissions=True)
                frappe.db.commit()


@frappe.whitelist()
def before_submit_bom(doc,method):
    doc.set("is_active",1)
    doc.set("is_default",1)
    today = datetime.now().strftime('%Y-%m-%d')
    after_3_days = add_to_date(datetime.now(), days=3, as_string=True)
    m={"doctype":"Material Request","material_request_type":"Manufacture"}
    m['schedule_date']=after_3_days
    m['set_warehouse']="Navya Store Office - NAVYA"
    mr=frappe.get_doc(m)
    row = mr.append("items", {})
    row.item_code=doc.item
    row.qty=1
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
    item_doc.save(ignore_permissions=True)


@frappe.whitelist()
def update_price_item(doc,method):
    item_doc=frappe.get_doc("Item",doc.item)
    if item_doc.ignore_project==1:
        item_doc.set("ignore_project",0)
    if item_doc.ignore_project==0:
        item_doc.set("ignore_project",1)
    item_doc.save(ignore_permissions=True)
