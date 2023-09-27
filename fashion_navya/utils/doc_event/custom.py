import frappe
from erpnext.stock.dashboard.item_dashboard import get_data
import json
from navya.api_folder.py.item_variants import create_multiple_variants_custom,create_variant_custom


@frappe.whitelist(allow_guest=True)
def make_rtw_item(doc,method):
	item_doc=frappe.get_doc("Item",doc.item)
	get_ptt=frappe.db.sql("""select name from `tabPattern` where docstatus=1 and item_code='{}'  """.format(doc.item),as_dict=1)
	if item_doc.rtw==1 or not  item_doc.variant_of:
		return


	check_smpl=doc.item.split("-")
	get_part=check_smpl[:-1]
	join_name="-".join(get_part)
	fjoin_item=join_name+"-RTW"
	if frappe.db.exists("Item",fjoin_item):
		return

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
		if len(get_ptt)!=0:
			for p in get_ptt:
				docpt=frappe.get_doc("Pattern",p['name'])
				dp=frappe.copy_doc(docpt)
				dp.set("item_code",variants.name)
				dp.set("workflow_state","Draft")
				dp.set("owner","Administrator")
				dp.insert(ignore_permissions=True)
				dp.submit()

		d=frappe.copy_doc(doc)
		print(variants.name,'aawwwwwww')
		d.set("item",variants.name)
		d.set("workflow_state","Draft")
		try:
			d.insert(ignore_permissions=True)
			d.submit()
			frappe.db.commit()

		except:
			pass

#sales ordr-sales order
@frappe.whitelist(allow_guest=True)
def make_rtw_item_pro(items=None):
	if not frappe.db.exists("Item",items):
		frappe.msgprint("Item Not exists")

	items_list=[]
	items_list.append(items)
	for m in items_list:
		item_doc=frappe.get_doc("Item",m)
		if item_doc.item_group!="Sample" or  not item_doc.variant_of:
			return
		get_ptt=frappe.db.sql("""select name from `tabPattern` where docstatus=1 and item_code='{}'  """.format(m),as_dict=1)
		get_bom=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and item='{}' and is_active=1 and is_default=1   """.format(m),as_dict=1)
		if item_doc.rtw==1 or not  item_doc.variant_of:
			return


		check_smpl=item_doc.name.split("-")
		if "RTW" in check_smpl:
			tr3="-".join(check_smpl)
			return tr3
	
		if "SMPL" in check_smpl:
			index =check_smpl.index("SMPL")
			check_smpl[index]="RTW"
			jrtw="-".join(check_smpl)
			if frappe.db.exists("Item",jrtw):
				return jrtw
			d={}
			for m in item_doc.attributes:
				if m.attribute!="Item Group":
					d[m.attribute]=m.attribute_value
			d['Item Group']="Ready To Wear"
			variants=create_variant_custom(item_doc.variant_of,d)
			if item_doc.project:
				variants.set("project",item_doc.project)


			if item_doc.image:
				variants.set("image",item_doc.image)


			variants.set("item_group","Ready Stock")
			check_item=frappe.db.sql("""select name from `tabItem` where item_code='{}'  """.format(variants.item_code),as_dict=1)
			if len(check_item)==0:
				variants.insert(ignore_permissions=True)
				if variants:
					return variants.name
			if len(check_item)!=0:
				return check_item[0]['name']

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
					d=frappe.copy_doc(bm)
					print(variants.name,'aawwwwwww')
					d.set("item",variants.name)
					d.set('pattern_not_required',1)
					d.set("workflow_state","Draft")
					try:
						d.insert(ignore_permissions=True)
						d.submit()
					except:
						pass
			


@frappe.whitelist(allow_guest=True)
def update_stock(values=None):
	val=json.loads(values)
	w=val['warehouse']
	items=frappe.db.sql("""select DISTINCT item_code from `tabBin` where warehouse='{}' and actual_qty >0  """.format(w),as_dict=1)
	if len(items)!=0:
		for i in items:
			doc=frappe.get_doc("Item",i['item_code'])
			nety=doc.net_stock_value or 0
			net_int=int(nety)
			net_stock=0
			net_stock_list=[0]
			get_stock=get_data(item_code=doc.name)
			if len(get_stock)!=0:
				for jk in get_stock:
					if jk['actual_qty']>0:
						net_stock_list.append(jk['actual_qty'])
					
			doc.set('net_stock_value',0)
			doc.set("net_stock_value",sum(net_stock_list))
			doc.save()


#from project
@frappe.whitelist(allow_guest=True)
def make_rtw_item_project(items=None):
	items=json.loads(items)
	for m in items:
		item_doc=frappe.get_doc("Item",m)
		get_ptt=frappe.db.sql("""select name from `tabPattern` where docstatus=1 and item_code='{}'  """.format(m),as_dict=1)
		get_bom=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and item='{}' and is_active=1 and is_default=1   """.format(m),as_dict=1)
		if item_doc.rtw==1 or not  item_doc.variant_of:
			return
		check_smpl=item_doc.name.split("-")
		get_part=check_smpl[:-1]
		join_nmae="-".join(get_part)
		fjoin_item=join_nmae+"-RTW"
		if frappe.db.exists("Item",fjoin_item):
			frappe.msgprint("Already exists")
			continue
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


			if item_doc.image:
				variants.set("image",item_doc.image)

			variants.set("item_group","Ready Stock")
			if frappe.db.exists('Item',variants.name):
				pass
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
					d=frappe.copy_doc(bm)
					print(variants.name,'aawwwwwww')
					d.set("item",variants.name)
					d.set('pattern_not_required',1)
					d.set("workflow_state","Draft")
					try:
						d.insert(ignore_permissions=True)
						d.submit()
					except:
						pass

			frappe.db.commit()
			frappe.msgprint("Item created successfully")
