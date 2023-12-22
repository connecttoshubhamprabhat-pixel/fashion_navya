import frappe
from erpnext.manufacturing.doctype.work_order.work_order import OverProductionError
import json
from erpnext.stock.get_item_details import get_conversion_factor
from erpnext.stock.utils import get_or_make_bin
from frappe import _, msgprint
from frappe.model.document import Document
from frappe.query_builder.functions import IfNull, Sum
from frappe.model.mapper import get_mapped_doc
from frappe.model.utils import get_fetch_values



@frappe.whitelist()
def make_work_order_project(items=None,doc=None,wqty=None):
    items=json.loads(items)
    created=[]
    if items:
        for i in items:
            item={"production_item":i,"fg_warehouse":"Navya Store Office - NAVYA"}
            item['wip_warehouse']="Sampling Unit - NAVYA"
            item['scrap_warehouse']="Navya Store Office - NAVYA"
            item['qty']=float(wqty) or 1
            get_bom=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and is_active=1 and is_default=1 and item='{}'  """.format(i),as_dict=1)
            if get_bom:
                item['bom_no']=get_bom[0]['name']
            else:
                frappe.msgprint("bom does not exist for {} ".format(i))
                continue
            wo = frappe.new_doc("Work Order")
            wo.update(item)
            wo.set_work_order_operations()
            wo.set_required_items()
            try:
                wo.flags.ignore_mandatory = True
                wo.flags.ignore_validate = True
                wo.insert()
                created.append("aa")
            except OverProductionError:
                pass
    if created:
        frappe.msgprint("Work order is created")



@frappe.whitelist()
def make_work_order_project(items=None,doc=None,wqty=None):
    items=json.loads(items)
    created=[]
    if items:
        for i in items:
            item={"production_item":i,"fg_warehouse":"Navya Store Office - NAVYA"}
            item['wip_warehouse']="Sampling Unit - NAVYA"
            item['scrap_warehouse']="Navya Store Office - NAVYA"
            item['qty']=float(wqty) or 1
            get_bom=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and is_active=1 and is_default=1 and item='{}'  """.format(i),as_dict=1)
            if get_bom:
                item['bom_no']=get_bom[0]['name']
            else:
                frappe.msgprint("bom does not exist for {} ".format(i))
                continue
            wo = frappe.new_doc("Work Order")
            wo.update(item)
            wo.set_work_order_operations()
            wo.set_required_items()
            try:
                wo.flags.ignore_mandatory = True
                wo.flags.ignore_validate = True
                wo.insert()
                created.append("aa")
            except OverProductionError:
                pass
    if created:
        frappe.msgprint("Work order is created")



@frappe.whitelist()
def todo_link_withproject(doc,method):
    if doc.reference_type=="Item":
        link_doc=frappe.get_doc("Item",doc.reference_name)
        if link_doc.project:
            doc.db_set("project",link_doc.project, update_modified=False)

    if doc.reference_type=="Purchase Order":
        link_doc=frappe.get_doc("Purchase Order",doc.reference_name)
        if link_doc.project:
            doc.db_set("project",link_doc.project, update_modified=False)

    if doc.reference_type=="Material Request":
        link_doc=frappe.get_doc("Material Request",doc.reference_name)
        if link_doc.project:
            doc.db_set("project",link_doc.project, update_modified=False)


    if doc.reference_type=="Work Order":
        link_doc=frappe.get_doc("Work Order",doc.reference_name)
        if link_doc.project:
            doc.db_set("project",link_doc.project, update_modified=False)

    if doc.reference_type=="Stock Entry":
        link_doc=frappe.get_doc("Stock Entry",doc.reference_name)
        if link_doc.project:
            doc.db_set("custom_project",link_doc.project, update_modified=False)


    if doc.reference_type=="Pattern":
        link_doc=frappe.get_doc("Pattern",doc.reference_name)
        if link_doc.project:
            doc.db_set("project",link_doc.project, update_modified=False)



    if doc.reference_type=="Task":
        link_doc=frappe.get_doc("Task",doc.reference_name)
        if link_doc.project:
            doc.db_set("project",link_doc.project, update_modified=False)



@frappe.whitelist()
def make_mv(source_name, target_doc = None):
    #frappe.msgprint("a")
    doc = get_mapped_doc(
        "Sales Order",
        source_name, {
            "Sales Order": {
                "doctype": "Maintenance Visit",
                "validation": {
                    "docstatus": ["=", 1]
                },
                "field_map": {
                    "name": "sales_order",
                    "customer": "customer",
                    "delivery_date": "custom_delivery_date",
                },
            },
            "Sales Order Item": {
                "doctype": "Maintenance Visit Purpose",
                "field_map": {
                    "item_code": "item_code",
                    "item_name": "item_name",
                    "description": "description",
                },
            },

        },
        target_doc,
    )

    return doc


@frappe.whitelist()
def get_mapped_subcontracting_order(source_name, target_doc=None):
    if target_doc and isinstance(target_doc, str):
        target_doc = json.loads(target_doc)
        for key in ["service_items", "items", "supplied_items"]:
            if key in target_doc:
                del target_doc[key]
        target_doc = json.dumps(target_doc)

    target_doc = get_mapped_doc(
		"Purchase Order",
		source_name,
		{
			"Purchase Order": {
				"doctype": "Subcontracting Order",
				"field_map": {},
				"field_no_map": ["total_qty", "total", "net_total"],
				"validation": {
					"docstatus": ["=", 1],
				},
			},
			"Purchase Order Item": {
				"doctype": "Subcontracting Order Service Item",
				"field_map": {},
				"field_no_map": [],
			},
		},
		target_doc,
	)


    target_doc.populate_items_table()
    if target_doc.set_warehouse:
        for item in target_doc.items:
            item.warehouse = target_doc.set_warehouse
    else:
        source_doc = frappe.get_doc("Purchase Order", source_name)
        if source_doc.set_warehouse:
            for item in target_doc.items:
                item.warehouse = source_doc.set_warehouse
        else:
            for idx, item in enumerate(target_doc.items):
                item.warehouse = source_doc.items[idx].warehouse



    print(target_doc,"target_doddddddddddddddddddddddddddc")
    target_doc.set("supplier_warehouse","Shamsudeen  - NAVYA")
    target_doc.save()
    target_doc.submit()
    frappe.db.commit()





@frappe.whitelist()
def cancel_mr_unlink(doc,method):
    if doc.references:
        frappe.msgprint("aa")
        if doc.references[0].reference_doctype=="Sales Order":
            so=doc.references[0].reference_name
            mr=frappe.db.sql("""select DISTINCT  parent from `tabMaterial Request Item` where sales_order='{}' and docstatus=1  """.format(so),as_dict=1)
            if mr:
                frappe.msgprint("aa1")
                for i in mr:
                    mrdoc=frappe.get_doc("Material Request",i['parent'])
                    mrdoc.set("status","Cancelled")
                    mrdoc.set("docstatus",2)
                    mrdoc.set("workflow_state","Cancelled")
                    mrdoc.save(ignore_permissions=True)


@frappe.whitelist()
def check_amount_so(doc,method):
    if doc.references:
        frappe.msgprint("aa")
        if doc.references[0].reference_doctype=="Sales Order":
            so=frappe.get_doc("Sales Order",doc.references[0].reference_name)
            if doc.paid_amount>so.grand_total:
                frappe.throw("Paid Amount is greater than Sales order Amount")
