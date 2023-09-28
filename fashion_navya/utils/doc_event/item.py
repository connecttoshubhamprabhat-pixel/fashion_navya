import frappe
from frappe import _
from frappe.utils import cstr, flt
from erpnext.stock.dashboard.item_dashboard import get_data
from erpnext.stock.utils import (
	is_reposting_item_valuation_in_progress,
	update_included_uom_in_report,
)



@frappe.whitelist(allow_guest=True)
def custom_title_fields(doc,method):
    if doc.item_code:
        #frappe.throw("custom_title_fields")
        docitem=frappe.get_doc("Item",doc.item_code)
        item=docitem.name
        net_stock=[0]
        get_stock=get_data(item_code=item)
        for jk in get_stock:
            if not jk['actual_qty']<0:
                net_stock.append(int(jk['actual_qty']))

        docitem.set("net_stock_value",0)

        docitem.db_set("net_stock_value",sum(net_stock), update_modified=False)
		#-------end-------------
        size=frappe.db.sql("""select attribute_value from `tabItem Variant Attribute` where attribute="Size" and parent='{}'  """.format(docitem.name),as_dict=1)
        if not size:
            data="Stock:{},Size:{}".format(sum(net_stock),'None')
            docitem.set('custom_title',data)
            frappe.db.set_value('Item',docitem.name,'custom_title',data, update_modified=False)
            frappe.db.commit()

        if size:
            size=size[0]['attribute_value']
            data="Stock:{},Size:{}".format(sum(net_stock) or 0,size)
            frappe.db.set_value('Item',docitem.name,'custom_title',data, update_modified=False)
            frappe.db.set_value('Item',docitem.name,'product_size',size, update_modified=False)
            frappe.db.commit()





@frappe.whitelist()
def change_description(doc,method):
	if doc.variant_of and len(doc.description) <50:
		doc.set("description"," ")
		if doc.variant_based_on == "Item Attribute":
			if doc.attributes:
				attributes_description =doc.custom_des+" "
				for d in doc.attributes:
					if d.attribute_value:
						if d.attribute not in ['Size','Item Group']:
							attributes_description += "<div>" + d.attribute + ": " + cstr(d.attribute_value) + "</div>"
				doc.db_set("description",attributes_description, update_modified=False)


@frappe.whitelist()
def change_description_old():
	get_item=frappe.db.sql(""" select name from `tabItem` where ignore_project=0 and is_customer_provided_item=0 and sync_item_via_nextwoocom=1  """,as_dict=1)
	if len(get_item)!=0:
		for  m in  get_item:
			print(m['name'])
			doc=frappe.get_doc("Item",m['name'])
			descus=doc.custom_des or " "
			if doc.ignore_project==0:
				doc.set("description"," ")
				if doc.variant_based_on == "Item Attribute":
					if doc.attributes:
						attributes_description =descus+" "
						for d in doc.attributes:
							if d.attribute_value:
								if d.attribute not in ['Size','Item Group']:
									attributes_description += "<div>" + d.attribute + ": " + cstr(d.attribute_value) + "</div>"

						doc.db_set("description",attributes_description, update_modified=False)
						try:
							doc.set("ignore_project",1)
							doc.save()
							frappe.db.commit()
						except:
							continue





@frappe.whitelist(allow_guest=True)
def delete_item_customise():
	get_items=frappe.db.sql("""select name from `tabItem` where creation >= NOW() - INTERVAL 2 DAY  and item_group='Customise' and variant_of is null  """,as_dict=1)
	if len(get_items)!=0:
		for i in get_items:
			print(i['name'],'aa')
			soi=frappe.db.sql(""" select item_code from `tabSales Order Item` where docstatus < 2 and item_code='{}'  """.format(i['name']),as_dict=1)
			if len(soi)==0:
				print(i['name'])
				doc=frappe.get_doc("Item",i['name'])
				doc.delete()
				frappe.db.commit()



@frappe.whitelist(allow_guest=True)
def delete_files(doc,method):
	f=frappe.db.sql(""" select name from `tabFile` where attached_to_doctype="Item" and attached_to_name='{}'   """.format(doc.name),as_dict=1)
	if len(f)!=0:
		for i in f:
			fdoc=frappe.get_doc("File",i['name'])
			fdoc.delete()
			frappe.db.commit()


@frappe.whitelist(allow_guest=True)
def custom_descrip(doc,method):
	if doc.custom_des and doc.has_variants==1:
		get_items=frappe.db.sql(""" select name from `tabItem` where variant_of='{}'   """.format(doc.name),as_dict=1)
		if len(get_items)!=0:
			for i in  get_items:
				vdoc=frappe.get_doc("Item",i['name'])
				vdoc.db_set("custom_des",doc.custom_des, update_modified=False)




@frappe.whitelist(allow_guest=True)
def renamedoc(doc,method):
    if doc.variant_of:
            old_docs=doc.get_doc_before_save()
            if doc and old_docs:
                    if doc.name and old_docs.name :
                            if old_docs.name!=doc.name:
                                    items=frappe.db.sql("""select name from `tabItem` where parent_item='{}'  """.format(old_docs.name),as_dict=1)
                                    if len(items)!=0:
                                            p=frappe.get_doc("Item",items[0]['name'])
                                            p.db_set("parent_item",doc.name, update_modified=False)
                                            p.save()


@frappe.whitelist(allow_guest=True)
def set_item_project_reorder(doc,method):
    item=doc.name
    split_name=item.split("-")
    if doc.variant_of and doc.project:
        if "RTW" in split_name:
            project=frappe.get_doc("Project",doc.project)
            exists=frappe.db.sql(""" select name from `tabReItems` where item_code='{}' and parent='{}' """.format(item,project.name),as_dict=1)
            if len(exists)==0:
                row = project.append("re_order", {})
                row.item_code=doc.name
                row.min=1
                project.save(ignore_permissions=True)

@frappe.whitelist(allow_guest=True)
def remove_item_rtw(doc,method):
    item=doc.name
    split_name=item.split("-")
    if doc.variant_of and doc.project:
        if "RTW" in split_name:
            exists=frappe.db.sql(""" select name from `tabReItems` where item_code='{}' and parent='{}' """.format(item,doc.project),as_dict=1)
            if len(exists)!=0:
                frappe.db.sql(""" delete from `tabReItems` where item_code='{}' and parent='{}' """.format(item,doc.project),as_dict=1)
                frappe.db.commit()



@frappe.whitelist(allow_guest=True)
def create_mr_reoder(doc,method):
    items=[]
    if doc.doctype=="Sales Invoices":
        if doc.is_pos or doc.update_stock:
            for i in doc.items:
                item=i.item_code.split("-")
                exists=frappe.db.sql(""" select name from `tabReItems` where item_code='{}' """.format(i.item_code),as_dict=1)
                if len(exists)!=0 and "RTW" in item:
                    qty=0
                    data=get_data(item_code=i.item_code)
                    if data:
                        for j in data:
                            if j['actual_qty']>0:
                                qty+=j['actual_qty']
                    if qty==0:
                        items.append(i.item_code)


    if doc.doctype=="Sales Order":
        for i in doc.items:
            item=i.item_code.split("-")
            exists=frappe.db.sql(""" select name from `tabReItems` where item_code='{}' """.format(i.item_code),as_dict=1)
            if len(exists)!=0 and "RTW" in item:
                qty=0
                data=get_data(item_code=i.item_code)
                if data:
                    for j in data:
                        if j['actual_qty']>0:
                            qty+=j['actual_qty']
                if qty==0:
                    items.append(i.item_code)


    #delivery # NOTE
    if doc.doctype=="Delivery Notes":
        for i in doc.items:
            item=i.item_code.split("-")
            exists=frappe.db.sql(""" select name from `tabReItems` where item_code='{}' """.format(i.item_code),as_dict=1)
            if len(exists)!=0 and "RTW" in item:
                qty=0
                data=get_data(item_code=i.item_code)
                if data:
                    for j in data:
                        if j['actual_qty']>0:
                            qty+=j['actual_qty']
                if qty==0:
                    items.append(i.item_code)


    if items:
        d={'doctype':"Material Request","material_request_type":"Manufacture"}
        mr=frappe.get_doc(d)
        for i in items:
            row = mr.append("items", {})
            row.item_code=i
            row.qty=1

        mr.insert()
        mr.submit()


@frappe.whitelist()
def report_stock_bal():
	is_reposting_item_valuation_in_progress()
	items=frappe.db.sql("""select name from `tabItem` where disabled=0 """,as_dict=1)
