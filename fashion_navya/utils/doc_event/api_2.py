import frappe
import json
from erpnext.stock.dashboard.item_dashboard import get_data
from datetime import datetime
from frappe.utils import add_to_date
from navya.api_folder.py.project import make_pattren_from_variant_so,bom_copy_so_enabled_item
import json
import re
from fashion_navya.utils.doc_event.item import make_kit_item
from navya.api_folder.py.item_variants import create_multiple_variants_custom,create_variant_custom


#smpl duplicate in project
@frappe.whitelist()
def make_smpl_sizes(values=None,items=None):
    values=json.loads(values)
    items=json.loads(items)
    print(items,'items')
    print(values,'values')
    size=values.get("size")
    if items:
        for i in items:
            item_doc=frappe.get_doc("Item",i)
            if not item_doc.variant_of:
                return
            d={}
            get_ptt=frappe.db.sql("""select name from `tabPattern` where docstatus=1 and item_code='{}'  """.format(i),as_dict=1)
            get_bom=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and item='{}' and is_active=1 and is_default=1   """.format(i),as_dict=1)
            for m in item_doc.attributes:
                if m.attribute!="Size":
                    d[m.attribute]=m.attribute_value
            d['Size']=size
            variants=create_variant_custom(item_doc.variant_of,d)
            if item_doc.project:
                variants.set("project",item_doc.project)

            if item_doc.image:
                variants.set("image",item_doc.image)

            variants.set("item_group","Sample")
            if frappe.db.exists('Item',variants.name):
                continue
            variants.save(ignore_permissions=True)
            if len(get_ptt)!=0:
                for p in get_ptt:
                    docpt=frappe.get_doc("Pattern",p['name'])
                    dp=frappe.copy_doc(docpt)
                    dp.set("item_code",variants.name)
                    dp.set("workflow_state","Draft")
                    try:
                        dp.insert(ignore_permissions=True)
                        dp.submit()
                    except:
                        pass

            if len(get_bom)!=0:
                for k in get_bom:
                    bm=frappe.get_doc("BOM",k['name'])
                    bom_copy_so_enabled_item(item_doc.name,variants.name)

            frappe.db.commit()
            frappe.msgprint("Item created successfully")




@frappe.whitelist()
def set_silvit_cus(doc,method):
    if not doc.get("__islocal") and not doc.measurement:
        mes=["Shoulder","Upper Bust","Cross Back","Cross front","Bust","Under Bust","Waist","Abdomen","Armhole","Bicep","Sleeve Length","Jacket Length","Bottom Waist","Hip","Crouch","Upper Thigh","Lower Thigh","knee","Ankle Mori","Bottom Length","Full Outfit Length","Top Length","Kurta Length"]
        for m  in mes:
            if frappe.db.exists("Measurements",m):
                row = doc.append("measurement", {})
                row.parameter = m
                row.round=0.0
                row.label=0.0




@frappe.whitelist()
def check_work_order_status(doc,method):
	for i in doc.items:
		if i.work_order:
			wo=frappe.get_doc("Work Order",i.work_order)
			if wo.docstatus==0:
				frappe.throw("Work Order is not submitted in Line Item:- {}".format(i.idx))




@frappe.whitelist()
def template_bom(doc,method):
	item=frappe.get_doc("Item",doc.item)
	if item.has_variants==1:
		supers=["amita@navya.biz","pawasthy11@gmail.com"]
		user=frappe.session.user
		if user not in supers:
			frappe.throw("Sorry Template Item you can not Approve")




#after insert
@frappe.whitelist()
def create_perm_exis(doc,method):
	if doc.event_name:
		for i in doc.items:
			get_w=frappe.db.sql("""select source_warehouse from `tabWexhibition` where source_warehouse='{}' and parent='PFL-2023-00009' and create=1  """.format(i.s_warehouse),as_dict=1)
			if len(get_w)==0:
				msg="No Permision for {}".format(i.s_warehouse)
				frappe.throw(msg)


#before submit
@frappe.whitelist()
def create_perm_submit(doc,method):
	if doc.event_name:
		for i in doc.items:
			get_w=frappe.db.sql("""select target_warehouse from `tabWexhibition` where target_warehouse='{}' and parent='PFL-2023-00009' and receive=1  """.format(i.t_warehouse),as_dict=1)
			if len(get_w)==0:
				msg="No Permision for {}".format(i.t_warehouse)
				frappe.throw(msg)



@frappe.whitelist()
def customer_added_mr(doc,method):
	for i in doc.items:
		if i.custom_customer and i.idx==1:
			doc.set("custom_customer",i.custom_customer)
		if i.sales_order and not i.custom_customer and i.idx==1:
			get_customer=frappe.db.sql("""select customer from `tabSales Order` where name='{}'   """.format(i.sales_order),as_dict=1)
			if get_customer:
				i.set("custom_customer",get_customer[0]['customer'])
				doc.set("custom_customer",get_customer[0]['customer'])




@frappe.whitelist()
def set_so_mr(doc,method):
	if doc.material_request:
		get_so=frappe.db.sql("""select *  from `tabMaterial Request` where docstatus<2 and name='{}'  """.format(doc.material_request),as_dict=1)
		if get_so:
			if get_so[0]['sales_order']:
				so=frappe.get_doc("Sales Order",get_so[0]['sales_order'])
				doc.set("sales_order",so.name)
				doc.set("customer",so.customer)



@frappe.whitelist()
def status_updated(doc,method):
	doc.db_set("custom_status",doc.satatus, update_modified=False)
