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
    if doc.variant_of and doc.project and frappe.db.exists("Item",doc.name):
        if "RTW" in split_name:
            project=frappe.get_doc("Project",doc.project)
            exists=frappe.db.sql(""" select name from `tabReItems` where item_code='{}' and parent='{}' """.format(item,project.name),as_dict=1)
            if len(exists)==0:
                row = project.append("re_order", {})
                row.item_code=doc.name
                row.min=1
                #project.save(ignore_permissions=True)

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
	if not doc.get("__islocal"):
		doc.custom_witem_stock=[]
		data=get_data(item_code=doc.name)
		all_child=[]
		if data:
			for j in data:
				if j['actual_qty']>0:
					row1 = doc.append("custom_witem_stock", {})
					row1.warehouse=j['warehouse']
					row1.qty=j['actual_qty']

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
	if not doc.taxes_and_charges or len(doc.taxes)==0:
		frappe.throw("Please add GST")
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
	if not image and not  name:
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
		if j.attribute not in ["Size","Item Group"]:
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
	split_doc=doc.name.split("-")
	split=doc.name.split("-")
	if split[-1]!="k":
		new_item=doc.name+"-k"
		d={'doctype':"Item","kit_item":1,"item_group":"M kit","stock_uom":"Nos","item_code":new_item,"image":doc.image}
		d['project']=doc.project
		if "RTW" in split_doc and "BPK"  not in split_doc:
			d['is_sub_contracted_item']=1
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
	user=frappe.session.user
	super_user=["amita@navya.biz","pawasthy11@gmail.com"]
	if items:
		d={"doctype":"Stock Entry","stock_entry_type":"Material Transfer"}
		d['rfse']="Stock Transfer"
		if sw=="Santushti - NAVYA":
			warehouses=frappe.db.sql("""select name from `tabWarehouse` where parent_warehouse='Santushti - NAVYA'  """,as_dict=1)
			for wc in warehouses:
				child_w.append(wc['name'])



		se=frappe.get_doc(d)
		if sw!="Santushti - NAVYA":
			exists=frappe.db.sql("""select name from `tabLocation Wise Warehoue`  where parent="PFL-2023-00001" and warehouse='{}' and user='{}'   """.format(sw,user),as_dict=1)
			if len(exists)==0 and user not in super_user:
				frappe.throw("You can't transfer from this warehouse")

			for i in items:
				row = se.append("items", {})
				row.item_code=i.get('name')
				row.s_warehouse=sw
				row.t_warehouse=tw
				row.qty=1

			se.insert()
			if se:
				frappe.msgprint("Created")
				return se.name


		if sw=="Santushti - NAVYA":
			for k in items:
				#frappe.msgprint(k.get("name"))
				stock=get_data(item_code=k.get("name"))
				w_new=[]
				child_w=list(set(child_w))
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
						exists=frappe.db.sql("""select name from `tabLocation Wise Warehoue`  where parent="PFL-2023-00001" and warehouse='{}' and user='{}'   """.format(m.get('warehouse'),user),as_dict=1)
						if len(exists)==0 and user not in super_user:
							msg="You can't transfer from this warehouse: {}".format(m.get("warehouse"))
							frappe.throw(msg)


						#qty_total=0
						#datas=get_data(item_code=k.get('name'),warehouse=m)
						#if datas:
						#	for d1 in datas:
						#		if d1['actual_qty']>0:
						#			qty_total+=d1['actual_qty']

						row = se.append("items", {})
						row.item_code=m.get("item_code")
						row.s_warehouse=m.get("warehouse")
						row.t_warehouse=tw
						row.qty=m.get("actual_qty")

			se.insert()
			#frappe.msgprint("Created")







@frappe.whitelist()
def make_new_item_sub(doc,method):
	for i in doc.items:
		old=frappe.get_doc("Item",i.item_code)
		split=old.name.split("-")
		item=i.item_code+"-"+doc.supplier
		d={'doctype':"Item","kit_item":1,"item_group":"M kit","stock_uom":"Nos","item_code":item,"image":doc.image}
		d['item_name']=old.item_name
		d['project']=old.project
		if "RTW" in split and "BPK" not in split:
			d['is_sub_contracted_item']=1
		new=frappe.get_doc(d)
		new.insert(ignore_permissions=True)

@frappe.whitelist()
def make_add_kt(doc,method):
	if not doc.get("__islocal"):
		split=doc.name.split("-")
		if not doc.variant_of and "k"==split[:-1]:
			s_add=split[0:-1]
			join="-".join(s_add)
			if frappe.db.exists("Item",join):
				olddoc=frappe.get_doc("Item",join)
				doc.set("parent_item",join)
				doc.set("project",olddoc.project)





@frappe.whitelist()
def make_kit_item_parent(doc,method):
	if doc.variant_of:
		new_item=doc.name+"-k"
		split=doc.name.split("-")
		if frappe.db.exists("Item",new_item):
			return

		d={'doctype':"Item","kit_item":1,"item_group":"M kit","stock_uom":"Nos","item_code":new_item,"image":doc.image}
		d['project']=doc.project
		d['item_name']=doc.item_name
		d['parent_item']=doc.name
		if "RTW" in  split and "BPK" not in split:
			d['is_sub_contracted_item']=0
		ndoc=frappe.get_doc(d)
		ndoc.insert(ignore_permissions=True)




@frappe.whitelist()
def make_kit_item_parent_save(doc,method):
	if not doc.get("__islocal") and doc.variant_of:
		new_item=doc.name+"-k"
		if frappe.db.exists("Item",new_item):
			return


		d={'doctype':"Item","kit_item":1,"is_sub_contracted_item":0,"item_group":"M kit","stock_uom":"Nos","item_code":new_item,"image":doc.image}
		d['project']=doc.project
		d['item_name']=doc.item_name
		d['parent_item']=doc.name
		ndoc=frappe.get_doc(d)
		ndoc.insert(ignore_permissions=True)


#fetch source warehouse se
@frappe.whitelist()
def fetch_source_se(items=None):
	items=json.loads(items)
	print(items,'items')
	item_dict=[]
	if items:
		for i in items:
			data=get_data(item_code=i)
			if data:
				for j in data:
					if j['actual_qty']>0:
						item_dict.append(j)

	return item_dict





#fetch source warehouse se
@frappe.whitelist()
def fetch_source_se_without(items=None):
	items=json.loads(items)
	print(items,'items')
	item_dict=[]
	if items:
		for i in items:
			data=get_data(item_code=i['item_code'])
			if data:
				for j in data:
					if j['actual_qty']>=i['qty']:
						j['actual_qty']=i['qty']
						item_dict.append(j)
						continue
	return item_dict



#march 16/2024
@frappe.whitelist(allow_guest=True)
def check_subconracted(doc,method):
	if not doc.variant_of:
		if doc.parent_item:
			if not frappe.db.exists("Item",doc.parent_item):
				doc.set("parent_item",None)


	if doc.custom_subcontracted:
		return
	if doc.variant_of:
		doc.set("is_sub_contracted_item",0)
	if doc.variant_of:
		doc.set("is_sales_item",1)
	items_groups=["Prototype","PP Sample"]
	if doc.item_group in items_groups:
		doc.set("is_sub_contracted_item",0)

	if doc.name:
		names=doc.name.split("-")
		if 'MTM' in names:
			doc.set("is_sub_contracted_item",1)



		if "SMPL" in names:
			if "HEK"  in names and "SMPL" in names:
				doc.set("is_sub_contracted_item",0)

			if "k"  in names or  "BPK" in names:
				doc.set("is_sub_contracted_item",0)


		if "PRSMPL" in names or "PPSMPL" in names:
			if "DPK" in names:
				doc.set("is_sub_contracted_item",1)
			else:
				doc.set("is_sub_contracted_item",0)

		if "RTW" in names and "BP" in names:
			if "HEK" in names or  "BPK" in names or "k" in names:
				doc.set("is_sub_contracted_item",0)

		if "DPK" in names:
			doc.set("is_sub_contracted_item",1)

		if "RTW" in names and not "BP" in names:
			if "BPK" in names:
				doc.set("is_sub_contracted_item",0)






@frappe.whitelist(allow_guest=True)
def make_bom_cr(items=None):
	items=json.loads(items)
	if items:
		for i in items:
			pmain_item=i.split("-")
			for p in range(len(pmain_item)):
				if pmain_item[p]=="RTW":
					pmain_item[p]="SMPL"

			pmain_item_join="-".join(pmain_item)
			get_bom_creator=frappe.db.sql("""select name from `tabBOM Creator` where item_code='{}' and docstatus=1 and status in ("In Progress","Completed")   ORDER BY  modified limit 1 """.format(pmain_item_join),as_dict=1)
			if len(get_bom_creator)!=0:
				make_duplicate_rtw(name=get_bom_creator[0]['name'])
				#frappe.db.commit()

			get_bom_creator_new=frappe.db.sql("""select name,custom_old_bomc from `tabBOM Creator` where item_code='{}' and docstatus=0  """.format(i),as_dict=1)
			if len(get_bom_creator_new)!=0:
				rebuild_refrences_submit(name=get_bom_creator_new[0]['name'],old=get_bom_creator_new[0]['custom_old_bomc'])









@frappe.whitelist(allow_guest=True)
def make_duplicate_rtw(name=None):
	old=frappe.get_doc("BOM Creator",name)
	new_bom=frappe.copy_doc(old)
	new_bom.set("custom_old_bomc",old.name)
	new_bom.set("status","Draft")
	pmain_item=old.item_code.split("-")
	for p in range(len(pmain_item)):
		if pmain_item[p]=="SMPL":
			pmain_item[p]="RTW"

	pmain_item_join="-".join(pmain_item)
	if frappe.db.exists("Item",pmain_item_join):
		new_bom.set("item_code",pmain_item_join)

	if new_bom.items:
		for y in new_bom.items:
			child_item=y.item_code.split("-")
			for h in range(len(child_item)):
				if child_item[h]=="SMPL":
					child_item[h]="RTW"
			child_item_join="-".join(child_item)
			if frappe.db.exists("Item",child_item_join):
				y.set("item_code",child_item_join)


			child_items=y.fg_item.split("-")
			for q in range(len(child_items)):
				if child_items[q]=="SMPL":
					child_items[q]="RTW"
			child_item_joins="-".join(child_items)
			if frappe.db.exists("Item",child_item_joins):
				y.set("fg_item",child_item_joins)


	new_bom.insert()
	frappe.msgprint("created")



@frappe.whitelist(allow_guest=True)
def rebuild_refrences(name=None,old=None):
	new=frappe.get_doc("BOM Creator",name)
	if new.custom_bomc==1:
		new.set("custom_bomc",0)
	else:
		new.set("custom_bomc",1)
	for i in new.items:
		get_row=frappe.db.sql(""" select idx from `tabBOM Creator Item` where name='{}' and docstatus=1 and parent='{}' """.format(i.fg_reference_id,old),as_dict=1)
		if len(get_row)!=0:
			#idx=int(get_row[0]['parent_row_no'])
			idx=get_row[0]['idx']
			get_row_new=frappe.db.sql(""" select name from `tabBOM Creator Item` where parent='{}' and idx='{}' """.format(name,idx),as_dict=1)
			if len(get_row_new)!=0:
				i.set("fg_reference_id",get_row_new[0]['name'])


	new.save()
	frappe.msgprint("rebuild")


@frappe.whitelist(allow_guest=True)
def rebuild_refrences_submit(name=None,old=None):
	new=frappe.get_doc("BOM Creator",name)
	if new.custom_bomc==1:
		new.set("custom_bomc",0)
	else:
		new.set("custom_bomc",1)
	for i in new.items:
		get_row=frappe.db.sql(""" select idx from `tabBOM Creator Item` where name='{}' and docstatus=1 and parent='{}' """.format(i.fg_reference_id,old),as_dict=1)
		if len(get_row)!=0:
			#idx=int(get_row[0]['parent_row_no'])
			idx=get_row[0]['idx']
			get_row_new=frappe.db.sql(""" select name from `tabBOM Creator Item` where parent='{}' and idx='{}' """.format(name,idx),as_dict=1)
			if len(get_row_new)!=0:
				i.set("fg_reference_id",get_row_new[0]['name'])


	new.save()
	new.db_set("custom_by_project",1, update_modified=False)
	new.submit()
	frappe.msgprint("rebuild")




@frappe.whitelist(allow_guest=True)
def submit_bom_rtw_bomc(doc,method):
	return
	# frappe.logger().debug("***ssssswwwwwwww")
	# if doc.bom_creator:
	# 	bomc=frappe.get_doc("BOM Creator",doc.bom_creator)

	# 	if bomc.custom_old_bomc:
	# 		boms=frappe.db.sql("""select name from `tabBOM` where docstatus=0 and bom_creator='{}' ORDER BY creation ASC """.format(doc.bom_creator),as_dict=1)
	# 		if len(boms)!=0:
	# 			for i in boms:
	# 				b=frappe.get_doc("BOM",i['name'])
	# 				bc=frappe.get_doc("BOM Creator",b.bom_creator)
	# 				if not bc.custom_bomc:
	# 					continue
	# 				name=doc.bom_creator
	# 				old=bc.custom_bomc
	# 				b.set("pattern_not_required",1)
	# 				pmain_item=b.item.split("-")
	# 				box=[]
	# 				if "SMPL" in pmain_item:
	# 					bom.append(3)
	# 					indx=pmain_item.index("SMPL")
	# 					pmain_item[indx]="RTW"


	# 				if "RTW" in pmain_item and not box:
	# 					indx=pmain_item.index("RTW")
	# 					pmain_item[indx]="SMPL"




	# 				join_name="-".join(pmain_item)
	# 				frappe.msgprint(join_name,"itemname")
	# 				get_bom_name=frappe.db.sql(""" select routing,name from `tabBOM` where docstatus<2 and item='{}' and  with_operations=1 and bom_creator='{}'  """.format(join_name,old),as_dict=1)
	# 				#frappe.throw(get_bom_name,"get_bom_name")
	# 				if len(get_bom_name)!=0:
	# 					bom_doc=frappe.get_doc("BOM",get_bom_name[0]['name'])
	# 					b.set("routing",bom_doc.routing)
	# 					frappe.msgprint(bom_doc.routing,"rount")
	# 					b.set("with_operations",1)
	# 					b.operations=[]
	# 					print(bom_doc.name,"nameeeeeeee")
	# 					for k in bom_doc.operations:
	# 						row = b.append("operations", {})
	# 						row.operation=k.operation
	# 						row.operating_cost=k.operating_cost
	# 						row.hour_rate=k.hour_rate
	# 						row.cost_per_unit=k.cost_per_unit
	# 						row.description=k.description
	# 						row.time_in_mins=k.time_in_mins
	# 						row.workstation=k.workstation
	# 						row.cost_per_unit=k.cost_per_unit
	# 						row.sequence_id=k.sequence_id


	# 					#b.save()
	# 					b.submit()
	# 					#frappe.msgprint("Saved")







@frappe.whitelist(allow_guest=True)
def size_changes_bomc(name=None,values=None):
	new=frappe.get_doc("BOM Creator",name)
	values=json.loads(values)
	size=values.get("size")
	name_split=new.item_code.split("-")
	sizes=["XS","S","M","L","XL","XXL","XXXL"]
	for m in name_split:
		if m in sizes:
			idx=name_split.index(m)
			name_split[idx]=size

	join_name="-".join(name_split)
	new.set("item_code",join_name)

	for i in new.items:
		a_1=i.item_code.split("-")
		a_2=i.fg_item.split("-")
		sizes=["XS","S","M","L","XL","XXL","XXXL"]
		for m in a_1:
			if m in sizes:
				idx=a_1.index(m)
				a_1[idx]=size

		for k in a_2:
			if k in sizes:
				idx=a_2.index(k)
				a_2[idx]=size

		a_1_join="-".join(a_1)
		a_2_join="-".join(a_2)
		i.set("item_code",a_1_join)
		i.set("fg_item",a_2_join)

	new.save()
	frappe.msgprint("Changed")






@frappe.whitelist(allow_guest=True)
def make_duplicate_smpl(name=None):
	old=frappe.get_doc("BOM Creator",name)
	new_bom=frappe.copy_doc(old)
	new_bom.set("custom_old_bomc",old.name)
	new_bom.set("status","Draft")
	new_bom.insert()
	frappe.msgprint("created")




@frappe.whitelist(allow_guest=True)
def color_changes(name=None,values=None):
	new=frappe.get_doc("BOM Creator",name)
	values=json.loads(values)
	size=values.get("size")
	name_split=new.item_code.split("-")
	print(name_split,'name_split')
	sizes=[]
	get_colors=frappe.db.sql("""select abbr from `tabItem Attribute Value` where parent="Colour" """,as_dict=1)
	if get_colors:
		for c in get_colors:
			sizes.append(c['abbr'])
	for m in name_split:
		if m in sizes:
			idx=name_split.index(m)
			name_split[idx]=size

	join_name="-".join(name_split)
	new.set("item_code",join_name)
	##print(join_name,'join_name')

	for i in new.items:
		a_1=i.item_code.split("-")
		a_2=i.fg_item.split("-")
		for m in a_1:
			if m in sizes:
				idx=a_1.index(m)
				a_1[idx]=size

		for k in a_2:
			if k in sizes:
				idx=a_2.index(k)
				a_2[idx]=size


		a_1_join="-".join(a_1)
		a_2_join="-".join(a_2)
		#print(a_1_join,'a_1_join')
		#print(a_2_join,'a_2_join')
		i.set("item_code",a_1_join)
		i.set("fg_item",a_2_join)

	new.save()
	frappe.msgprint("Changed")



@frappe.whitelist(allow_guest=True)
def submit_bom_rtw_bomc_manul(name=None,old=None):
	boms=frappe.db.sql("""select name from `tabBOM` where docstatus=0 and bom_creator='{}' ORDER BY creation ASC """.format(name),as_dict=1)
	if len(boms)!=0:
		for i in boms:
			new=frappe.get_doc("BOM",i['name'])
			old_bomc=frappe.get_doc("BOM Creator",old)
			item_doc=frappe.get_doc("Item",new.item)
			split_name=item_doc.name.split("-")
			if item_doc.variant_of:
				get_bom_name=frappe.db.sql("""select name from `tabBOM` where item='{}' and docstatus=1 and bom_creator='{}' """.format(old_bomc.item_code,old),as_dict=1)
				if len(get_bom_name)!=0:
					submit_bom_op(new=new.name,old=get_bom_name[0]['name'])
				else:
					print()
					#pass
					frappe.throw("BOM is not Submit yet")

			if "BPK" in split_name:
				get_bom_name=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and bom_creator='{}' and item like '%BPK%' """.format(old),as_dict=1)
				if len(get_bom_name)!=0:
					submit_bom_op(new=new.name,old=get_bom_name[0]['name'])
				else:
					frappe.throw("BOM is not Submit yet")


			if "DPK" in split_name:
				get_bom_name=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and bom_creator='{}' and item like '%DPK%' """.format(old),as_dict=1)
				if len(get_bom_name)!=0:
					submit_bom_op(new=new.name,old=get_bom_name[0]['name'])
				else:
					#pass
					frappe.throw("BOM is not Submit yet")


			if "HEK" in split_name:
				get_bom_name=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and bom_creator='{}' and item like '%HEK%' """.format(old),as_dict=1)

				if len(get_bom_name)!=0:
					submit_bom_op(new=new.name,old=get_bom_name[0]['name'])
				else:
					#pass
					frappe.throw("BOM is not Submit yet")

			if "k" in split_name:
				get_bom_name=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and bom_creator='{}' and item like '%-k%' """.format(old),as_dict=1)
				if len(get_bom_name)!=0:
					submit_bom_op(new=new.name,old=get_bom_name[0]['name'])
				else:
					#pass
					frappe.throw("BOM is not Submit yet")











@frappe.whitelist(allow_guest=True)
def submit_bom_op(new=None,old=None):
	new=frappe.get_doc("BOM",new)
	old=frappe.get_doc("BOM",old)
	new.db_set("pattern_not_required",1, update_modified=False)
	split_name=new.item.split("-")
	if "k" in split_name and "RTW" in split_name:
		new.set("routing","Main KIT RTW")

	elif "k" in split_name and "SMPL" in split_name:
		new.set("routing","Main KIT SMPL")

	elif "HEK" in split_name and "RTW" in split_name:
		new.set("routing","HEK RTW")

	elif "HEK" in split_name and "SMPL" in split_name:
		new.set("routing","HEK SMPL")

	else:
		new.db_set("routing",old.routing)

	new.set("with_operations",1)
	new.submit()
	frappe.msgprint("operations added and submit")



@frappe.whitelist(allow_guest=True)
def color_sizes_changes(name=None,values=None):
	new=frappe.get_doc("BOM Creator",name)
	values=json.loads(values)
	size=values.get("size")
	color=values.get("color")

	name_split=new.item_code.split("-")
	sizes=[]
	colors=[]
	get_colors=frappe.db.sql("""select abbr from `tabItem Attribute Value` where parent="Colour" """,as_dict=1)
	get_sizes=frappe.db.sql("""select abbr from `tabItem Attribute Value` where parent="Size" """,as_dict=1)

	if get_colors:
		for c in get_colors:
			colors.append(c['abbr'])

	if get_sizes:
		for s in get_sizes:
			sizes.append(s['abbr'])
	for m in name_split:
		if m in sizes:
			idx=name_split.index(m)
			name_split[idx]=size

	for c in name_split:
		if c in colors:
			idx=name_split.index(c)
			name_split[idx]=color


	join_name="-".join(name_split)
	new.set("item_code",join_name)

	for i in new.items:
		a_1=i.item_code.split("-")
		a_2=i.fg_item.split("-")
		for m in a_1:
			if m in sizes:
				idx=a_1.index(m)
				a_1[idx]=size

		for m in a_1:
			if m in colors:
				idx=a_1.index(m)
				a_1[idx]=color


		for k in a_2:
			if k in sizes:
				idx=a_2.index(k)
				a_2[idx]=size

		for k in a_2:
			if k in colors:
				idx=a_2.index(k)
				a_2[idx]=color

		a_1_join="-".join(a_1)
		a_2_join="-".join(a_2)
		i.set("item_code",a_1_join)
		i.set("fg_item",a_2_join)

	new.save()
	frappe.msgprint("Changed")


#fetch pattern fabric
@frappe.whitelist(allow_guest=True)
def fabric_fetch_pattt(doc,method):
	if not doc.get("__islocal") and doc.custom_nof==0:
		name=doc.name
		docs=frappe.get_doc("BOM Creator",doc.name)
		item_last_row=doc.items[-1].fg_item
		get_fabric_item=frappe.db.sql(""" select item_code from `tabBOM Creator Item` where parent='{}' and fg_item='{}' """.format(name,item_last_row),as_dict=1)
		fabrics=[]
		if get_fabric_item:
			for f in get_fabric_item:
				fabrics.append(f['item_code'])

		#get fabrice of list
		#fetch pattern
		get_apptern_pattern=frappe.db.sql("""select name from `tabPattern` where item_code='{}' and sheet_no=2 and docstatus=1  """.format(doc.item_code),as_dict=1)
		if not get_apptern_pattern:
			frappe.msgprint("Pattern missing")

		fabric_non_exists=[]
		row_remove=[]
		fab_exists=[]
		get_last_row_details=doc.items[-1]
		if get_apptern_pattern:
			pattern_name=get_apptern_pattern[0]['name']
			for i in doc.items:
				if i.item_code in fabrics:
					fab_exists.append(i.item_code)
					get_fabric_qty=frappe.db.sql("""select qty from `tabFabric Pattern` where item_code='{}' and parent='{}'  """.format(i.item_code,pattern_name),as_dict=1)
					if get_fabric_qty:
						i.db_set("qty",get_fabric_qty[0]['qty'], update_modified=False)
					else:
						if len(get_apptern_pattern)!=0:
							ptt_doc_n=frappe.get_doc("Pattern",get_apptern_pattern[0]['name'])
							if ptt_doc_n.fabrices:
								doc.items.remove(i)

		if len(get_apptern_pattern)!=0:
			ptt_doc=frappe.get_doc("Pattern",get_apptern_pattern[0]['name'])
			new_items=[]
			for w in doc.items:
				if w.fg_item==item_last_row:
					new_items.append(w.item_code)

			if ptt_doc.fabrices:
				for pf in ptt_doc.fabrices:
					if pf.item_code not in fab_exists and pf.item_code not in new_items:

						row=doc.append("items", {})
						row.item_code=pf.item_code
						row.qty=pf.qty
						row.fg_item=item_last_row
						row.fg_reference_id=get_last_row_details.fg_reference_id
						row.item_group=get_last_row_details.item_group








frappe.whitelist(allow_guest=True)
def submit_bom_project(doc,method):
	if doc.bom_creator:
		bomc=frappe.get_doc("BOM Creator",doc.bom_creator)
		if bomc.custom_by_project==0:
			return
		doc.set("with_operations",1)
		split=doc.item.split("-")
		if "DPK" in split:
			doc.set("routing","DPK")

		if "BPK" in split and "HE" in split:
			doc.set("routing","BPK with Dyeing")

		if "BPK" in split and  not "HE" in split:
			doc.set("routing","BPK without Dyeing")


		if "k" in split and "RTW" in split:
			doc.set("routing","Main KIT RTW")


		if "k" in split and "SMPL" in split:
			doc.set("routing","Main KIT SMPL")


		item=frappe.get_doc("Item",doc.item)
		if item.variant_of:
			doc.set("routing","Final BOM")


		if "HEK" in split and "RTW" in split:
			doc.set("routing","HEK RTW")

		if "HEK" in split and "SMPL" in split:
			doc.set("routing","HEK SMPL")

		doc.submit()





frappe.whitelist(allow_guest=True)
def set_reorder_new(doc,method):
	if doc.variant_of and doc.item_group=="Ready Stock":
		doc.reorder_levels=[]
		size=[]
		split_parent=doc.variant_of.split("-")[-1]
		for i in doc.attributes:
			if i.attribute=="Size":
				size.append(i.attribute_value)
				break

		get_val=frappe.db.sql("""select capacity from `tabCapacity  Silhouette` where parent='{}' and parentfield="ready"  and sizes='{}'  """.format(split_parent,size[0]),as_dict=1)
		if get_val:
			capacity=get_val[0]['capacity']
			get_shops=frappe.db.sql("""select name from `tabWarehouse` where parent_warehouse='Shops - NAVYA'   """,as_dict=1)
			shops=[]
			if get_shops:
				for s in get_shops:
					shops.append(s['name'])

			shops=list(set(shops))
			manufactures_qty=capacity*len(shops)
			#set re order for level manufacture
			row = doc.append("reorder_levels", {})
			row.warehouse_group="Sainik Farm - NAVYA"
			row.material_request_type="Manufacture"
			row.warehouse_reorder_level=capacity
			row.warehouse_reorder_qty=capacity
			row.warehouse="Navya Store Office - NAVYA"

			for i in shops:
				if i=="Pune - NAVYA":
					row1 = doc.append("reorder_levels", {})
					row1.warehouse_group="Pune - NAVYA"
					row1.material_request_type="Transfer"
					row1.warehouse_reorder_level=capacity
					row1.warehouse_reorder_qty=capacity
					row1.warehouse="PStore - NAVYA"

				if i=="Santushti - NAVYA":
					row2 = doc.append("reorder_levels", {})
					row2.warehouse_group="Santushti - NAVYA"
					row2.material_request_type="Transfer"
					row2.warehouse_reorder_level=capacity
					row2.warehouse_reorder_qty=capacity
					row2.warehouse="SStore - NAVYA"


frappe.whitelist(allow_guest=True)
def set_reorder_new_smpl(doc,method):
	if doc.variant_of and doc.item_group=="Sample":
		doc.reorder_levels=[]
		get_shops=frappe.db.sql("""select name from `tabWarehouse` where parent_warehouse='Shops - NAVYA'   """,as_dict=1)
		shops=[]
		if get_shops:
			for s in get_shops:
				shops.append(s['name'])

		shops=list(set(shops))
		#set re order for level manufacture
		row = doc.append("reorder_levels", {})
		row.warehouse_group="Sainik Farm - NAVYA"
		row.material_request_type="Manufacture"
		row.warehouse_reorder_level=1
		row.warehouse_reorder_qty=1
		row.warehouse="Navya Store Office - NAVYA"

		for i in shops:
			if i=="Pune - NAVYA":
				row1 = doc.append("reorder_levels", {})
				row1.warehouse_group="Pune - NAVYA"
				row1.material_request_type="Transfer"
				row1.warehouse_reorder_level=1
				row1.warehouse_reorder_qty=1
				row1.warehouse="PStore - NAVYA"

			if i=="Santushti - NAVYA":
				row2 = doc.append("reorder_levels", {})
				row2.warehouse_group="Santushti - NAVYA"
				row2.material_request_type="Transfer"
				row2.warehouse_reorder_level=1
				row2.warehouse_reorder_qty=1
				row2.warehouse="SStore - NAVYA"



#fetch source warehouse se
@frappe.whitelist()
def fetch_source_me(name=None):
	if not name:
		return

	doc=frappe.get_doc("Material Request",name)
	items=doc.items
	if not doc.set_from_warehouse:
		frappe.throw("Please set first Source Warehouse")
	w=[]
	wdoc=frappe.get_doc("Warehouse",doc.set_from_warehouse)
	if wdoc.is_group==0:
		w.append(wdoc.name)
	else:
		get_w=frappe.db.sql("""select  DISTINCT name from `tabWarehouse`  where parent_warehouse='{}' and disabled=0 """.format(wdoc.name),as_dict=1)
		if get_w:
			for k in get_w:
				w.append(k['name'])
	yes_save=[]
	if items:
		doc.items=[]
		for i in items:

			for j in w:
				get_bin=frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code='{}' and warehouse='{}' """.format(i.item_code,j),as_dict=1)
				if len(get_bin)!=0:
					if get_bin[0]['qty']!=None:
						if get_bin[0]['qty']>0:
							yes_save.append("ys")
							row = doc.append("items", {})
							row.item_code=i.item_code
							row.qty=get_bin[0]['qty']
							row.from_warehouse=j
	if yes_save:
		doc.save(ignore_permissions=True)
		frappe.msgprint("Updated")



@frappe.whitelist(allow_guest=True)
def re_order_set_item_wise(items=None):
	items=json.loads(items)
	make=[]
	if items:
		for i in items:
			doc=frappe.get_doc("Item",i)
			if doc.item_group=="Sample":
				set_reorder_new_smpl_project(name=i)
				make.append("aa")

			if doc.item_group=="Ready Stock":
				#frappe.msgprint(i)
				set_reorder_rtw(name=i)
				make.append("12")

	if make:
		frappe.msgprint("Re-Order Set")


@frappe.whitelist(allow_guest=True)
def set_reorder_project_wise(name=None):
	doc=frappe.get_doc("Project",name)
	if not doc.custom_wop:
		frappe.throw("Work orders Item table is empty")

	for i in doc.custom_wop:
		if i.manufactured==1:
			item=frappe.get_doc("Item",i.item)
			if item.variant_of:
				if item.item_group=="Ready Stock":
					set_reorder_rtw(name=item.name)
					frappe.msgprint("Updated for Ready Stock")

				if item.item_group=="Sample":
					set_reorder_new_smpl_project(name=item.name)
					frappe.msgprint("Updated for Sample")


@frappe.whitelist(allow_guest=True)
def set_reorder_set_bulk(names=None):
	names=json.loads(names)
	for name in names:
		doc=frappe.get_doc("Project",name)
		get_items=frappe.db.sql("""select DISTINCT name from `tabItem` where project='{}' and variant_of is not null  """.format(doc.name),as_dict=1)
		if get_items:
			for i in get_items:
				item=frappe.get_doc("Item",i['name'])
				if item.variant_of:
					if item.item_group=="Ready Stock":
						set_reorder_rtw(name=item.name)
						frappe.msgprint("Updated for Ready Stock")
					if item.item_group=="Sample":
						set_reorder_new_smpl_project(name=item.name)
						frappe.msgprint("Updated for Sample")





@frappe.whitelist(allow_guest=True)
def set_reorder_rtw(name=None):
	doc=frappe.get_doc("Item",name)
	if doc.variant_of and doc.item_group=="Ready Stock":
		doc.reorder_levels=[]
		size=[]
		split_parent=doc.variant_of.split("-")[-1]
		for i in doc.attributes:
			if i.attribute=="Size":
				size.append(i.attribute_value)
				break

		get_val=frappe.db.sql("""select capacity from `tabCapacity  Silhouette` where parent='{}' and parentfield="ready"  and sizes='{}'  """.format(split_parent,size[0]),as_dict=1)
		if get_val:
			capacity=get_val[0]['capacity']
			get_shops=frappe.db.sql("""select name from `tabWarehouse` where parent_warehouse='Shops - NAVYA'   """,as_dict=1)
			shops=[]
			if get_shops:
				for s in get_shops:
					shops.append(s['name'])



			shops=list(set(shops))
			manufactures_qty=capacity*len(shops)
			capacity_shops=capacity/2
			#set re order for level manufacture
			split=name.split("-")
			row = doc.append("reorder_levels", {})
			row.warehouse_group="All Warehouses - NAVYA"
			row.material_request_type="Manufacture"
			row.warehouse_reorder_level=3
			row.warehouse_reorder_qty=3
			row.warehouse="Navya Store Office - NAVYA"



			for i in shops:
				if i=="Pune - NAVYA":
					row1 = doc.append("reorder_levels", {})
					row1.warehouse_group="Pune - NAVYA"
					row1.material_request_type="Transfer"
					row1.warehouse_reorder_level=1
					row1.warehouse_reorder_qty=1
					row1.warehouse="PStore - NAVYA"

				if i=="Santushti - NAVYA":
					row2 = doc.append("reorder_levels", {})
					row2.warehouse_group="Santushti - NAVYA"
					row2.material_request_type="Transfer"
					row2.warehouse_reorder_level=1
					row2.warehouse_reorder_qty=1
					row2.warehouse="SStore - NAVYA"

				if i=="Sainik Farm - NAVYA":
					row2 = doc.append("reorder_levels", {})
					row2.warehouse_group="Sainik Farm - NAVYA"
					row2.material_request_type="Transfer"
					row2.warehouse_reorder_level=1
					row2.warehouse_reorder_qty=1
					row2.warehouse="Main Storage - NAVYA"


	if doc.reorder_levels:
		doc.save()
		frappe.db.commit()
		#frappe.msgprint("Updated")





frappe.whitelist(allow_guest=True)
def set_reorder_new_smpl_project(name=None):
	doc=frappe.get_doc("Item",name)
	if doc.variant_of and doc.item_group=="Sample":
		doc.reorder_levels=[]
		get_shops=frappe.db.sql("""select name from `tabWarehouse` where parent_warehouse='Shops - NAVYA'   """,as_dict=1)
		shops=[]
		if get_shops:
			for s in get_shops:
				shops.append(s['name'])

		shops=list(set(shops))
		#set re order for level manufacture
		row = doc.append("reorder_levels", {})
		row.warehouse_group="All Warehouses - NAVYA"
		row.material_request_type="Manufacture"
		row.warehouse_reorder_level=2
		row.warehouse_reorder_qty=1
		row.warehouse="Navya Store Office - NAVYA"

		for i in shops:
			if i=="Pune - NAVYA":
				row1 = doc.append("reorder_levels", {})
				row1.warehouse_group="Pune - NAVYA"
				row1.material_request_type="Transfer"
				row1.warehouse_reorder_level=0
				row1.warehouse_reorder_qty=1
				row1.warehouse="PStore - NAVYA"

			if i=="Santushti - NAVYA":
				row2 = doc.append("reorder_levels", {})
				row2.warehouse_group="Santushti - NAVYA"
				row2.material_request_type="Transfer"
				row2.warehouse_reorder_level=0
				row2.warehouse_reorder_qty=1
				row2.warehouse="SStore - NAVYA"

			if i=="Sainik Farm - NAVYA":
				row2 = doc.append("reorder_levels", {})
				row2.warehouse_group="Sainik Farm - NAVYA"
				row2.material_request_type="Transfer"
				row2.warehouse_reorder_level=0
				row2.warehouse_reorder_qty=1
				row2.warehouse="Main Storage - NAVYA"


	if doc.reorder_levels:
		doc.save()
		frappe.db.commit()






@frappe.whitelist()
def set_validation_bomc(doc,method):
    if doc.custom_old_bomc:
        bomc=frappe.get_doc("BOM Creator",doc.custom_old_bomc)
        if bomc.status in ["Failed","Submitted"]:
            frappe.throw("  The status of the Old BOM Creator should neither be `failed` nor `submitted.` ")



@frappe.whitelist(allow_guest=True)
def make_bom_cr_prsmpl(items=None):
	items=json.loads(items)
	if items:
		for i in items:
			pmain_item=i.split("-")
			for p in range(len(pmain_item)):
				if pmain_item[p]=="SMPL":
					pmain_item[p]="PRSMPL"

			pmain_item_join="-".join(pmain_item)
			get_bom_creator=frappe.db.sql("""select name from `tabBOM Creator` where item_code='{}' and docstatus=1 and status in ("In Progress","Completed")   ORDER BY  modified limit 1 """.format(pmain_item_join),as_dict=1)
			if len(get_bom_creator)!=0:
				make_duplicate_prsmpl(name=get_bom_creator[0]['name'])
				#frappe.db.commit()
			else:
				frappe.msgprint("BOMC Is not found")

			get_bom_creator_new=frappe.db.sql("""select name,custom_old_bomc from `tabBOM Creator` where item_code='{}' and docstatus=0  """.format(i),as_dict=1)
			if len(get_bom_creator_new)!=0:
				rebuild_refrences_insert(name=get_bom_creator_new[0]['name'],old=get_bom_creator_new[0]['custom_old_bomc'])



@frappe.whitelist(allow_guest=True)
def make_duplicate_prsmpl(name=None):
	old=frappe.get_doc("BOM Creator",name)
	new_bom=frappe.copy_doc(old)
	new_bom.set("custom_old_bomc",old.name)
	new_bom.set("status","Draft")
	pmain_item=old.item_code.split("-")
	for p in range(len(pmain_item)):
		if pmain_item[p]=="PRSMPL":
			pmain_item[p]="SMPL"

	pmain_item_join="-".join(pmain_item)
	if frappe.db.exists("Item",pmain_item_join):
		new_bom.set("item_code",pmain_item_join)

	if new_bom.items:
		for y in new_bom.items:
			child_item=y.item_code.split("-")
			for h in range(len(child_item)):
				if child_item[h]=="PRSMPL":
					child_item[h]="SMPL"
			child_item_join="-".join(child_item)
			if frappe.db.exists("Item",child_item_join):
				y.set("item_code",child_item_join)


			child_items=y.fg_item.split("-")
			for q in range(len(child_items)):
				if child_items[q]=="PRSMPL":
					child_items[q]="SMPL"
			child_item_joins="-".join(child_items)
			if frappe.db.exists("Item",child_item_joins):
				y.set("fg_item",child_item_joins)


	new_bom.insert()
	frappe.msgprint("created")




@frappe.whitelist(allow_guest=True)
def rebuild_refrences_insert(name=None,old=None):
	new=frappe.get_doc("BOM Creator",name)
	if new.custom_bomc==1:
		new.set("custom_bomc",0)
	else:
		new.set("custom_bomc",1)
	for i in new.items:
		get_row=frappe.db.sql(""" select idx from `tabBOM Creator Item` where name='{}' and docstatus=1 and parent='{}' """.format(i.fg_reference_id,old),as_dict=1)
		if len(get_row)!=0:
			#idx=int(get_row[0]['parent_row_no'])
			idx=get_row[0]['idx']
			get_row_new=frappe.db.sql(""" select name from `tabBOM Creator Item` where parent='{}' and idx='{}' """.format(name,idx),as_dict=1)
			if len(get_row_new)!=0:
				i.set("fg_reference_id",get_row_new[0]['name'])


	new.save()
	new.db_set("custom_by_project",1, update_modified=False)
	#new.submit()
	frappe.msgprint("rebuild")



@frappe.whitelist(allow_guest=True)
def make_price_from_template(doc,method):
	doc.set("workflow_state","Approved")
	item_doc=frappe.get_doc("Item",doc.item_code)
	if item_doc.has_variants==1:
		get_items=frappe.db.sql("""select DISTINCT name from `tabItem` where variant_of='{}' """.format(doc.item_code),as_dict=1)
		if len(get_items)!=0 and doc.name:
			doc_name=frappe.get_doc("Item Price",doc.name)
			for i in get_items:
				item=i['name']
				new=frappe.copy_doc(doc_name)
				new.item_code=item
				exists=frappe.db.sql(""" select name from `tabItem Price` where item_code='{}' """.format(item),as_dict=1)
				if len(exists)==0:
					try:
						new.insert(ignore_permissions=True)
					except:
						pass


#source warehouse stock count
@frappe.whitelist(allow_guest=True)
def check_stock_count(doc,method):
	admin_users=['amita@navya.biz','pawasthy11@gmails.com']
	stock_entry_type=['Material Transfer','Material Transfer for Manufacture']
	user=frappe.session.user
	if user not in admin_users and doc.stock_entry_type in stock_entry_type and doc.ignore_custom==0:
		for i in doc.items:
			get_bin=frappe.db.sql("""select sum(actual_qty) as qty from  `tabBin`  where item_code='{}' and warehouse='{}'  and  actual_qty>0    """.format(i.item_code,i.s_warehouse),as_dict=1)
			if len(get_bin)!=0:
				if get_bin[0]['qty']!=None:
					if i.qty>get_bin[0]['qty']:
						msg="Out Of Stock,row:-{},Actual Stock in {},:-{}".format(i.idx,i.s_warehouse,get_bin[0]['qty'])
						frappe.throw(msg)
