import frappe
from erpnext.stock.dashboard.item_dashboard import get_data
from datetime import datetime
from frappe.utils import add_to_date
from navya.api_folder.py.project import make_pattren_from_variant_so,bom_copy_so_enabled_item
import json
import re
from fashion_navya.utils.doc_event.item import make_kit_item
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
def make_rtw_item_so(items=None,so=None):
	if not items:
		return

	items_list=json.loads(items)
	for m in items_list:
		item_doc=frappe.get_doc("Item",m)
		if item_doc.item_group!="Sample" or  not item_doc.variant_of:
			return
		get_ptt=frappe.db.sql("""select name from `tabPattern` where docstatus=1 and item_code='{}'  """.format(m),as_dict=1)
		get_bom=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and item='{}' and is_active=1 and is_default=1   """.format(m),as_dict=1)
		if item_doc.rtw==1 or not  item_doc.variant_of:
			return

		template=frappe.get_doc("Item",item_doc.variant_of)
		yes_item_group=[]
		for u in template.attributes:
			if u.attribute=="Item Group":
				yes_item_group.append("yes")
		if not yes_item_group:
			row=template.append("attributes", {})
			row.attribute="Item Group"
			template.save(ignore_permissions=True)

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
		if len(check_item)!=0:
			return check_item[0]['name']

		variants.save(ignore_permissions=True)
		if variants:
			make_ptt_so(smpl=item_doc.name,new=variants.name)
			#make_bom(smpl=item_doc.name,new=variants.name)
			bom_copy_so_enabled_item(item_doc.name,variants.name)
			return variants.name






@frappe.whitelist(allow_guest=True)
def make_bom(smpl=None,new=None):
	get_bom=frappe.db.sql("""select DISTINCT name from `tabBOM` where docstatus=1 and item='{}' and is_active=1 and is_default=1   """.format(smpl),as_dict=1)
	if len(get_bom)!=0:
		for k in get_bom:
			print(k['name'],"mybom")
			bm=frappe.get_doc("BOM",k['name'])
			d=frappe.copy_doc(bm)
			d.set("item",new)
			d.set('pattern_not_required',1)
			d.set("workflow_state","Draft")
			try:
				d.insert(ignore_permissions=True)
				d.submit()
			except:
				pass

@frappe.whitelist(allow_guest=True)
def make_ptt_so(smpl=None,new=None):
	get_ptt=frappe.db.sql("""select name from `tabPattern` where docstatus=1 and item_code='{}'  """.format(smpl),as_dict=1)
	if len(get_ptt)!=0:
		for p in get_ptt:
			docpt=frappe.get_doc("Pattern",p['name'])
			dp=frappe.copy_doc(docpt)
			dp.set("item_code",new)
			dp.set("workflow_state","Draft")
			try:
				dp.insert(ignore_permissions=True)
				dp.submit()
			except:
				continue






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


			bom_copy_so_enabled_item(item_doc.name,variants.name)

			frappe.db.commit()
			frappe.msgprint("Item created successfully")



@frappe.whitelist()
def make_customer_items(items=None,customer=None,rate=0,so=None):
	perdoc=frappe.get_doc("Permitted Files","PFL-2023-00008")
	if int(perdoc.cms)>int(rate):
		frappe.msgprint("The Price is less then 10000")
		return

	if not customer:
		frappe.msgprint("Please select customer")
		return



	customer_count=[]
	cs=customer.split(" ")
	if len(cs)>1:
		cs=customer.split(" ")
		dx=[]
		for c in cs:
			if c.strip():
				dx.append(c[0])
		if dx:
			customer_count.append(dx[0]+dx[1])
	else:
		customer_count.append(customer[0])



	items=json.loads(items)
	sizes=[]
	all_item=[]
	if frappe.db.exists("Item Attribute","Size"):
		att=frappe.get_doc("Item Attribute","Size")
		for j in att.item_attribute_values:
			sizes.append(j.abbr)

	for i in items:
		doc=frappe.get_doc("Item",i)
		CLEANR = re.compile('<.*?>')
		cleantext = re.sub(CLEANR, '',doc.description)
		if doc.item_group=="Sample" and doc.variant_of:
			check_name=doc.name+"-"+customer_count[0]
			if frappe.db.exists("Item",check_name):
				return check_name
			split_items=i.split("-")
			sizes=list(set(sizes))
			for s in split_items:
				if s in sizes:
					index =split_items.index(s)
					split_items[index]="C"
				if "SMPL"==s:
					split_items.remove(s)

			name="-".join(split_items)

			item_code=name+"-"+customer_count[0]
			if frappe.db.exists("Item",item_code):
				return item_code
			d={'doctype':"Item","item_group":"Customise","project":doc.project ,"stock_uom":doc.stock_uom,"image":doc.image}
			d['item_code']=item_code
			#d['item_name']=doc.item_name+"-"+customer
			d['item_name']=doc.item_name
			d['parent_item']=doc.name
			d['image']=doc.image
			d['customise']=1
			d['description']=cleantext
			n=frappe.get_doc(d)
			row =n.append("customer_list", {})
			row.customer=customer
			n.save(ignore_permissions=True)
			n.db_set("description",cleantext, update_modified=False)
			make_kit_item(name=n.name)
			make_price_doc(item=n.name,rate=rate)
			make_pattren_from_variant_so(doc.name,n.name)
			bom_copy_so_enabled_item(doc.name,n.name)
			all_item.append(n.name)

	if all_item:
		return all_item[-1]




@frappe.whitelist(allow_guest=True)
def make_made_tmso(items=None,customer=None,rate=0,so=None):
	perdoc=frappe.get_doc("Permitted Files","PFL-2023-00008")
	if int(perdoc.mtm)>int(rate):
		frappe.msgprint("The Price is less then 15000")
		return

	if not customer:
		frappe.msgprint("Please select customer")
		return

	customer_count=[]
	cs=customer.split(" ")
	if len(cs)>1:
		dx=[]
		for c in cs:
			if c.strip():
				dx.append(c[0])
		if dx:
			customer_count.append(dx[0]+dx[1])
	else:
		customer_count.append(customer[0])



	items=json.loads(items)
	size=[]
	all_item=[]
	if frappe.db.exists("Item Attribute","Size"):
		att=frappe.get_doc("Item Attribute","Size")
		for j in att.item_attribute_values:
			print(j.abbr)
			size.append(j.abbr)

	for i in items:
		doc=frappe.get_doc("Item",i)
		CLEANR = re.compile('<.*?>')
		cleantext = re.sub(CLEANR, '',doc.description)
		if doc.item_group=="Sample" and doc.variant_of:
			check_name=doc.name+"-"+customer_count[0]
			if frappe.db.exists("Item",check_name):
				return check_name
			split_items=i.split("-")
			sizes=list(set(size))
			print(sizes)
			for s in split_items:
				print(s,'sssss')
				if s in sizes:
					print('3599999999')
					index =split_items.index(s)
					split_items[index]="MTM"
				if "SMPL"==s:
					print("3567889")
					split_items.remove(s)

			name="-".join(split_items)
			print(name,'nameeeeeeeeeeeeeeeeeeeeeeeee')

			item_code=name+"-"+customer_count[0]
			if frappe.db.exists("Item",item_code):
				return item_code
			d={'doctype':"Item","item_group":"Customise","project":doc.project ,"stock_uom":doc.stock_uom,"image":doc.image}
			d['item_code']=item_code
			d['item_name']=name+"-"+customer
			d['parent_item']=doc.name
			d['customise']=1
			d['image']=doc.image
			d['description']=cleantext
			n=frappe.get_doc(d)
			row =n.append("customer_list", {})
			row.customer=customer
			n.save(ignore_permissions=True)
			if n:
				n.db_set("parent_item",doc.name, update_modified=False)
				n.db_set("description",cleantext, update_modified=False)
				make_kit_item(name=n.name)
				make_price_doc(item=n.name,rate=rate)
				make_pattren_from_variant_so(doc.name,n.name)
				bom_copy_so_enabled_item(doc.name,n.name)
				all_item.append(n.name)

	if all_item:
		return all_item[-1]




@frappe.whitelist()
def make_price_doc(item=None,rate=None):
	if not item and rate==0:
		return

	today = datetime.now().strftime('%Y-%m-%d')
	before_2_days = add_to_date(datetime.now(), days=-2, as_string=True)
	d={"doctype":"Item Price","item_code":item,"price_list":"Selling"}
	d['price_list_rate']=rate
	ip=frappe.get_doc(d)
	ip.save(ignore_permissions=True)
	ip.db_set("workflow_state","Approved", update_modified=False)
	ip.db_set("valid_from",before_2_days, update_modified=False)
	frappe.msgprint("Item created successfully")


@frappe.whitelist()
def name_fetch_wo(doc,method):
	if doc.custom_parent_item and not doc.custom_pname and doc.docstatus==0:
		if frappe.db.exists("Item",doc.custom_parent_item):
			item=frappe.get_doc("Item",doc.custom_parent_item)
			doc.set("custom_pname",item.item_name)



#item name rename with size
@frappe.whitelist()
def rename_item_with_size(doc,method):
	if doc.cms:
		for i in doc.items:
			if i.item_type=="Customize":
				if not i.size:
					frappe.throw("Size missing for Customise")

				item=frappe.get_doc("Item",i.item_code)
				name=item.item_name.split("-")
				d=re.findall(r'\d+',item.item_code)
				join_d="-".join(d)
				size="-C"+str(i.size)
				final_name=join_d+str(size)+"-"+name[-1]
				item.set('item_name',final_name)
				item.save(ignore_permissions=True)
				i.set('item_name',final_name)
