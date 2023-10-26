import frappe
from frappe import _
import json
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
def make_mr_manufacture(doc,method):
	items=[]
	print()
	if doc.doctype=="Sales Invoices":
		if doc.is_pos or doc.update_stock:
			for i in doc.items:
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
	print()




@frappe.whitelist()
def fetched_warehouse_qty(values=None):
	#is_reposting_item_valuation_in_progress()
	values=json.loads(values)
	item_group=values.get("item_group")
	if not item_group:
		return
	all_items=[]
	items=frappe.db.sql("""select name from `tabItem` where disabled=0 and item_group='{}' """.format(item_group),as_dict=1)
	if items:
		for i in items:
			all_items.append(i['name'])
	if all_items:
		for j in all_items:
			if frappe.db.exists("Item",j):
				doc=frappe.get_doc("Item",j)
				if doc.ignore_project==1:
					doc.set("ignore_project",0)
				else:
					doc.set("ignore_project",1)
				doc.save()
				frappe.db.commit()

		frappe.msgprint("updated successfully")




@frappe.whitelist()
def fetched_warehouse_qty_w(doc,method):
	if frappe.db.exists("Item",doc.name):
		data=get_data(item_code=doc.name)
		if len(data)!=0:
			doc.custom_witem_stock=[]
			for j in data:
				if j['actual_qty']>0:
					check_warehouse=frappe.db.sql(""" select name from `tabWarehouse` where parent_warehouse='Santushti - NAVYA' and name='{}' """.format(j['warehouse']),as_dict=1)
					row = doc.append("custom_witem_stock", {})
					row.warehouse=j['warehouse']
					row.qty=j['actual_qty']
					if len(check_warehouse)!=0:
						row1 = doc.append("custom_witem_stock", {})
						row1.warehouse="Santushti - NAVYA"
						row1.qty=j['actual_qty']
		else:
			doc.custom_witem_stock=[]



@frappe.whitelist()
def fetched_warehouse_sch(values=None):
	is_reposting_item_valuation_in_progress()
	all_items=[]
	items=frappe.db.sql("""select name from `tabItem` where disabled=0 and item_group in ('Sample','Ready Stock')  """,as_dict=1)
	if items:
		for i in items:
			all_items.append(i['name'])

	if all_items:
		for j in all_items:
			if frappe.db.exists("Item",j):
				doc=frappe.get_doc("Item",j)
				if doc.ignore_project==1:
					doc.set("ignore_project",0)
				else:
					doc.set("ignore_project",1)
				doc.save(ignore_permissions=True)


@frappe.whitelist()
def update_item(doc,method):
	for i in doc.items:
		item=frappe.get_doc("Item",i.item_code)
		if item.ignore_project==1:
			item.set("ignore_project",0)
		else:
			item.set("ignore_project",1)
		item.save(ignore_permissions=True)

@frappe.whitelist()
def update_images_item(name=None,image=None):
	if not name or  not image:
		return
	doc=frappe.get_doc("Item",name)
	template=doc.variant_of
	if not template:
		return
	size=[]
	for i in doc.attributes:
		if i.attribute=="Size":
			size.append(i.attribute_value)

	template=doc.variant_of
	images_items=[]
	get_child_items=frappe.db.sql("""select name from `tabItem` where variant_of='{}' and disabled=0 and name!='{}' """.format(template,name),as_dict=1)
	if get_child_items:
		for k in get_child_items:
			child=frappe.get_doc("Item",k['name'])
			for i in child.attributes:
				if i.attribute=="Size":
					if i.attribute_value in size:
						images_items.append(k['name'])
	for m in images_items:
		print(m,'mmmmmmmmmmmmm')
		image_doc=frappe.get_doc("Item",m)
		image_doc.db_set("image",image, update_modified=False)
		image_doc.save(ignore_permissions=True)


@frappe.whitelist()
def update_item_si(doc,method):
	if doc.update_stock:
		for i in doc.items:
			item=frappe.get_doc("Item",i.item_code)
			if item.ignore_project==1:
				item.set("ignore_project",0)
			else:
				item.set("ignore_project",1)
				item.save(ignore_permissions=True)


#fetch with same size of attributes
@frappe.whitelist()
def images_same_attributes(image=None,name=None):
	if not image and name:
		return
	doc=frappe.get_doc("Item",name)
	items=[]
	get_items=frappe.db.sql("""select name from `tabItem` where variant_of='{}' and disabled=0 """.format(doc.variant_of),as_dict=1)
	if get_items:
		for i in get_items:
			if i['name'] not in items and doc.name!=i['name']:
				items.append(i['name'])

	att_list=[]
	item_to_update=[]
	for j in doc.attributes:
		if j.attribute!="Size":
			d={}
			d['attribute']=j.attribute
			d['attribute_value']=j.attribute_value
			att_list.append(d)

	print(att_list,'att_list')

	for i in items:
		print(i,'iiiiiiiiiiii')
		item=frappe.get_doc("Item",i)
		item_att=item.attributes
		matched=0
		for m in att_list:
			print(m,'m')
			if m['attribute']!="Size":
				att_exists=frappe.get_all('Item Variant Attribute', filters ={'parent':i,"attribute":m['attribute'],"attribute_value":m['attribute_value']},fields = ['parent'])
				if len(att_exists)!=0:
					print(att_exists,'att_exists')
					matched+=1

		print(matched,'matched')
		print(len(att_list),"att_list")
		if matched==len(att_list):
			item_to_update.append(i)

	if item_to_update:
		print(item_to_update,'item_to_update')
		for k in item_to_update:
			item_doc=frappe.get_doc("Item",k)
			item_doc.db_set("image",image, update_modified=False)
			item_doc.save(ignore_permissions=True)







@frappe.whitelist()
def make_kit_item(name=None):
	if not name:
		return

	doc=frappe.get_doc("Item",name)
	split=doc.name.split("-")
	if split[-1]!="k":
		new_item=doc.name+"-k"
		d={'doctype':"Item","kit_item":1,"is_sub_contracted_item":1,"item_group":"M kit","stock_uom":"Nos","item_code":new_item,"image":doc.image}
		d['project']=doc.project
		d['item_name']=doc.item_name
		ndoc=frappe.get_doc(d)
		ndoc.save(ignore_permissions=True)

@frappe.whitelist()
def make_se_entry(items=None,values=None):
	items=json.loads(items)
	values=json.loads(values)
	sw=values.get("s_warehouse")
	tw=values.get("t_warehouse")
	child_w=[]
	if items:
		d={"doctype":"Stock Entry","stock_entry_type":"Material Transfer"}
		d['rfse']="Stock Transfer"
		if sw=="Santushti - NAVYA":
			warehouses=frappe.db.sql("""select name from `tabWarehouse` where parent_warehouse='Santushti - NAVYA'  """,as_dict=1)
			for wc in warehouses:
				child_w.append(wc['name'])

		se=frappe.get_doc(d)
		if sw!="Santushti - NAVYA":
			for i in items:
				row = se.append("items", {})
				row.item_code=i.get('name')
				row.s_warehouse=sw
				row.t_warehouse=tw
			se.insert()
			if se:
				frappe.msgprint("Created")
				return se.name

		if sw=="Santushti - NAVYA":
			for k in items:
				frappe.msgprint(k.get("name"))
				stock=get_data(item_code=k.get("name"))
				w_new=[]
				if len(stock)!=0:
					for j in stock:
						if j['actual_qty']>0 and j['warehouse'] in child_w:
							w_new.append(j)
				else:
					frappe.msgprint("Item is  not in Santushti: {}".format(k.get('name')))
					continue
				if not w_new:
					frappe.msgprint("Item is  not in Santushti: {}".format(k.get('name')))
					continue
				if w_new:
					for m in w_new:
						row = se.append("items", {})
						row.item_code=m.get('item_code')
						row.s_warehouse=m.get("warehouse")
						row.t_warehouse=tw
			se.insert()
			#frappe.msgprint("Created")







@frappe.whitelist()
def make_new_item_sub(doc,method):
	for i in doc.items:
		old=frappe.get_doc("Item",i.item_code)
		item=i.item_code+"-"+doc.supplier
		d={'doctype':"Item","kit_item":1,"is_sub_contracted_item":1,"item_group":"M kit","stock_uom":"Nos","item_code":item,"image":doc.image}
		d['item_name']=old.item_name
		d['project']=old.project
		new=frappe.get_doc(d)
		new.insert(ignore_permissions=True)
