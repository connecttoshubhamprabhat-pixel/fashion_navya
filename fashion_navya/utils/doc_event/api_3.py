import frappe
from erpnext.manufacturing.doctype.work_order.work_order import OverProductionError
import json
from erpnext.stock.get_item_details import get_conversion_factor
from erpnext.stock.utils import get_or_make_bin
from frappe import _, msgprint
from frappe.model.document import Document
from frappe.query_builder.functions import IfNull, Sum



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
