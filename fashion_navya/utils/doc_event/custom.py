import frappe
import json
from navya.api_folder.py.item_variants import create_multiple_variants_custom,create_variant_custom


@frappe.whitelist(allow_guest=True)
def make_rtw_item(doc,method):
    #smpl_bom=frappe.get_doc("BOM",doc.name)
    item_doc=frappe.get_doc("Item",doc.item)
    get_ptt=frappe.db.sql("""select name from `tabPattern` where docstatus=1 and item_code='{}'  """.format(doc.item),as_dict=1)
    if item_doc.rtw==1 or not  item_doc.variant_of:
        return
    check_smpl=doc.item.split("-")
    if "SMPL" in check_smpl:
        d={}
        for m in item_doc.attributes:
            if m.attribute!="Item Group":
                d[m.attribute]=m.attribute_value

        d['Item Group']="Ready To Wear"
        variants=create_variant_custom(item_doc.variant_of,d)
        if doc.project:
            variants.set("project",item_doc.project)

        variants.set("item_group","Ready Stock")
        variants.save(ignore_permissions=True)
        #smpl_bom.set("item",variants.name)
        #tabPattern
        if len(get_ptt)!=0:
            for p in get_ptt:
                docpt=frappe.get_doc("Pattern",p['name'])
                dp=frappe.copy_doc(docpt)
                dp.set("item_code",variants.name)
                dp.set("workflow_state","Draft")
                dp.insert(ignore_permissions=True)
                dp.submit()



            d=frappe.copy_doc(doc)
            print(variants.name,'aawwwwwww')
            d.set("item",variants.name)
            d.set("docstatus",1)
            d.set("workflow_state","Draft")
            d.insert(ignore_permissions=True)
            d.submit()

        frappe.db.commit()
        frappe.msgprint("Item created successfully")

@frappe.whitelist(allow_guest=True)
def make_rtw_item_pro(items=None):
    items=json.loads(items)
    #smpl_bom=frappe.get_doc("BOM",doc.name)for m in items:
    for m in items:
        item_doc=frappe.get_doc("Item",m)
        get_ptt=frappe.db.sql("""select name from `tabPattern` where docstatus=1 and item_code='{}'  """.format(m),as_dict=1)
        if item_doc.rtw==1 or not  item_doc.variant_of:
            return
        check_smpl=item_doc.name.split("-")
        if "SMPL" in check_smpl:
            print('59999999999999999999999999')
            d={}
            for m in item_doc.attributes:
                if m.attribute!="Item Group":
                    d[m.attribute]=m.attribute_value

            d['Item Group']="Ready To Wear"
            variants=create_variant_custom(item_doc.variant_of,d)
            if item_doc.project:
                variants.set("project",item_doc.project)

            variants.set("item_group","Ready Stock")
            variants.save(ignore_permissions=True)
            #smpl_bom.set("item",variants.name)
            #tabPattern
            if len(get_ptt)!=0:
                for p in get_ptt:
                    docpt=frappe.get_doc("Pattern",p['name'])
                    dp=frappe.copy_doc(docpt)
                    dp.set("item_code",variants.name)
                    dp.set("workflow_state","Draft")
                    dp.insert(ignore_permissions=True)
                    dp.submit()



                d=frappe.copy_doc(item_doc)
                print(variants.name,'aawwwwwww')
                d.set("item",variants.name)
                d.set("docstatus",1)
                d.set("workflow_state","Draft")
                d.insert(ignore_permissions=True)
                d.submit()

            frappe.db.commit()
            frappe.msgprint("Item created successfully")
