import frappe
import json

@frappe.whitelist()
def make_mr_project(name=None):
	if not name:
		return


	get_alls=frappe.db.sql("""select DISTINCT  name from `tabItem` where variant_of is not null and  project='{}'  """.format(name),as_dict=1)
	if get_alls:
		d={"doctype":"Material Request","material_request_type":"Manufacture","project":name}
		mr=frappe.get_doc(d)
		for i in get_alls:
			row = mr.append("items", {})
			row.item_code=i['name']
			row.description=i['name']
			row.uom="Nos"
			row.qty=1

		mr.insert()
		frappe.msgprint("MR Created")





@frappe.whitelist()
def make_mr_select(items=None,name=None):
	items=json.loads(items)
	if not name:
		return

	if items:
		d={"doctype":"Material Request","material_request_type":"Manufacture","project":name}
		mr=frappe.get_doc(d)
		for i in  items:
			row = mr.append("items", {})
			row.item_code=i
			row.description=i
			row.uom="Nos"
			row.qty=1

		mr.insert()
		frappe.msgprint("MR Created")







@frappe.whitelist()
def check_bom_mr(doc,method):
	bom_not_exists=[]
	for i in doc.items:
		check_bom=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and is_active=1 and is_default=1 and item='{}'  """.format(i.item_code),as_dict=1)
		if len(check_bom)==0:
			bom_not_exists.append("yes")

		if i.sales_order:
			doc.set("custom_is_so",1)

		split_code=i.item_code.split("-")
		if "MTM" in split_code:
			doc.set("custom_mtm",1)

		get_so_cms=frappe.db.sql("""select name from `tabSales Order Item` where item_type='Customize'  and  docstatus=1 and name='{}' and parent='{}'   """.format(i.sales_order_item,i.sales_order),as_dict=1)
		if len(get_so_cms)!=0:
			doc.set("custom_cms",1)
			
	if not bom_not_exists:
		doc.set("custom_bom",1)





@frappe.whitelist()
def check_bom_mr_old():

	get_mr=frappe.db.sql("""select 	DISTINCT parent from `tabMaterial Request Item` where sales_order is not null   """,as_dict=1)
	if get_mr:
		for m in get_mr:
			print(m['parent'])
			doc=frappe.get_doc("Material Request",m['parent'])
			for i in doc.items:
				check_bom=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and is_active=1 and is_default=1 and item='{}'  """.format(i.item_code),as_dict=1)
				if len(check_bom)!=0:
					#doc.set("custom_bom",1)
					frappe.db.sql("""update `tabMaterial Request` set custom_bom=1 where name='{}'  """.format(doc.name))

				if i.sales_order:
					#doc.set("custom_is_so",1)
					frappe.db.sql("""update `tabMaterial Request` set custom_is_so=1 where name='{}'  """.format(doc.name))

				split_code=i.item_code.split("-")
				if "MTM" in split_code:
					#doc.set("custom_mtm",1)
					frappe.db.sql("""update `tabMaterial Request` set custom_mtm=1 where name='{}'  """.format(doc.name))

				get_so_cms=frappe.db.sql("""select name from `tabSales Order Item` where item_type='Customize'  and  docstatus=1 and name='{}' and parent='{}'   """.format(i.sales_order_item,i.sales_order),as_dict=1)
				if len(get_so_cms)!=0:
					#doc.set("custom_cms",1)
					frappe.db.sql("""update `tabMaterial Request` set custom_cms=1 where name='{}'  """.format(doc.name))
				frappe.db.commit()





@frappe.whitelist()
def check_is_bom_mr(doc,method):
	if doc.is_active and doc.is_default:
		get_mr=frappe.db.sql(""" select DISTINCT  parent from `tabMaterial Request Item` where item_code='{}' and docstatus<2  """.format(doc.item),as_dict=1)
		if len(get_mr)!=0:
			for i in get_mr:
				frappe.db.sql("""update `tabMaterial Request` set custom_bom=1 where name='{}' and docstatus<2  """.format(i['parent']),as_dict=1)
				frappe.db.commit()


#on canel
@frappe.whitelist()
def uncheck_is_bom_mr(doc,method):
	check_bom=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and item='{}' and is_active=1 and is_default=1  """.format(doc.item),as_dict=1)
	if len(check_bom)==0:
		get_mr=frappe.db.sql(""" select DISTINCT  parent from `tabMaterial Request Item` where item_code='{}' and docstatus<2  """.format(doc.item),as_dict=1)
		if len(get_mr)!=0:
			for i in get_mr:
				frappe.db.sql("""update `tabMaterial Request` set custom_bom=0 where name='{}' and docstatus<2  """.format(i['parent']),as_dict=1)
				frappe.db.commit()



@frappe.whitelist()
def automated_mr_se(doc,method):
	if doc.items and doc.stock_entry_type=="Material Transfer" and doc.custom_skip_mr==0:
		mr_exists=doc.items[0].material_request
		if mr_exists:
			doc.set("add_to_transit",1)
			doc.set("custom_automated_mr",1)

#link so mr both
@frappe.whitelist()
def mr_links_transfer(doc,method):
	so_list=[]
	for i in doc.items:
		if i.sales_order not in so_list:
			so_list.append(i.sales_order)
	if so_list:
		for i in so_list:
			if doc.material_request_type=="Manufacture":
				get_mr_transfer=frappe.db.sql("""select DISTINCT parent from `tabMaterial Request Item`  where sales_order='{}' and parent in (select name from `tabMaterial Request` where docstatus<2 and material_request_type='Material Transfer' )  """.format(i),as_dict=1)
				if get_mr_transfer:
					frappe.db.sql("""update `tabMaterial Request` set custom_mrm='{}' where name='{}' and docstatus<2  """.format(doc.name,get_mr_transfer[0]['parent']))
					frappe.db.commit()

			if doc.material_request_type=="Material Transfer":
				get_mr_transfers=frappe.db.sql("""select DISTINCT parent from `tabMaterial Request Item`  where sales_order='{}' and parent in (select name from `tabMaterial Request` where docstatus<2 and material_request_type='Manufacture' )  """.format(i),as_dict=1)
				if get_mr_transfers:
					doc.set("custom_mrm",get_mr_transfers[0]['parent'])




@frappe.whitelist()
def check_bom_project(doc,method):
	bom_not_exists=[]
	for i in doc.items:
		get_bom=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and item='{}' and is_active=1 and is_default=1  """.format(i.item_code),as_dict=1)
		if len(get_bom)==0:
			bom_not_exists.append("yes")
	
	if not bom_not_exists:
		doc.set("custom_bom",1)






@frappe.whitelist()
def check_bom_project_old():
	mr=frappe.db.sql("""select name from `tabMaterial Request`   where material_request_type='Manufacture' and docstatus=1 and custom_bom=0  """,as_dict=1)
	if mr:
		for m in mr:
			doc=frappe.get_doc("Material Request",m['name'])
			for i in doc.items:
				get_bom=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and item='{}'  """.format(i.item_code),as_dict=1)
				if len(get_bom)!=0:
					frappe.db.sql("""update `tabMaterial Request` set custom_bom=1 where name='{}'  """.format(m['name']))
					frappe.db.commit()



#calander mr
@frappe.whitelist()
def get_events_mr(start, end, filters=None):
	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions("Material Request", filters)

	data = frappe.db.sql(
		"""
		select
			distinct `tabMaterial Request`.name, IFNULL(`tabMaterial Request Item`.custom_customer,`tabMaterial Request Item`.project) as customer, `tabMaterial Request`.status,
			`tabMaterial Request`.material_request_type as purpose, `tabMaterial Request`.schedule_date
		from
			`tabMaterial Request`, `tabMaterial Request Item`
		where `tabMaterial Request`.name = `tabMaterial Request Item`.parent
			and (ifnull(`tabMaterial Request Item`.schedule_date, '0000-00-00')!= '0000-00-00') \
			and (`tabMaterial Request Item`.schedule_date between %(start)s and %(end)s)
			and `tabMaterial Request`.docstatus < 2
			{conditions}
		""".format(
			conditions=conditions
		),
		{"start": start, "end": end},
		as_dict=True,
		update={"allDay": 0},
	)

	return data


@frappe.whitelist()
def project_wise_divide(name=None):
	doc=frappe.get_doc("Material Request",name)
	projects=frappe.db.sql("""select DISTINCT project from `tabMaterial Request Item`  where docstatus<2 and parent='{}'   """.format(name),as_dict=1)
	if projects:
		for pro in projects:
			project=pro['project']
			if_items=[]
			d={"doctype":"Material Request","material_request_type":doc.material_request_type,"project":project}
			items=frappe.db.sql("""select * from `tabMaterial Request Item`  where docstatus<2 and parent='{}' and project='{}'   """.format(name,project),as_dict=1)
			if items:
				mr=frappe.get_doc(d)
				if_items.append("a")
				for i in items:
					row = mr.append("items", {})
					row.item_code=i['item_code']
					row.description=i['description']
					row.uom="Nos"
					row.qty=1
					
				mr.insert()
				frappe.msgprint("Created")
			
@frappe.whitelist()
def project_wise_divide_auto():
	get_mr_list=frappe.db.sql("""select name  from `tabMaterial Request`  where docstatus=1 and material_request_type='Manufacture' and status='Pending' and project is null  and custom_is_so=0   """,as_dict=1)
	if len(get_mr_list)!=0:
		for m in get_mr_list:
			doc=frappe.get_doc("Material Request",m['name'])
			if doc.project:
				print()
				continue
			name=m['name']
			print(name)
			cancel_list=[]
			projects=frappe.db.sql("""select DISTINCT project from `tabMaterial Request Item`  where docstatus<2 and parent='{}'   """.format(name),as_dict=1)
			if len(projects)>1:
				for pro in projects:
					project=pro['project']
					if_items=[]
					d={"doctype":"Material Request","material_request_type":doc.material_request_type,"project":project,"custom_original_mr":name}
					items=frappe.db.sql("""select * from `tabMaterial Request Item`  where docstatus<2 and parent='{}' and project='{}'   """.format(name,project),as_dict=1)
					if items:
						mr=frappe.get_doc(d)
						if_items.append("a")
						for i in items:
							row = mr.append("items", {})
							row.item_code=i['item_code']
							row.description=i['description']
							row.uom="Nos"
							row.qty=1
						
						try:
							mr.insert()
							mr.submit()
							cancel_list.append(name)
							frappe.db.commit()
						except:
							continue
			#cancel mr
			if name in cancel_list:
				try:		
					doc.cancel()
					frappe.db.commit()
				except:
					continue


	
@frappe.whitelist()
def project_update_mr():
	get_mr_list=frappe.db.sql("""select name  from `tabMaterial Request`  where docstatus=1 and material_request_type='Manufacture' and status='Pending' and project is null """,as_dict=1)
	if len(get_mr_list)!=0:
		for m in get_mr_list:
			doc=frappe.get_doc("Material Request",m['name'])
			for i in doc.items:
				print(i.item_code)
				item=frappe.get_doc("Item",i.item_code)
				frappe.db.sql(""" update `tabMaterial Request Item` set project='{}'   where parent='{}' and idx='{}' """.format(item.project,doc.name,i.idx))
				frappe.db.commit()

@frappe.whitelist()
def reset_reorder(items=None):
	items=json.loads(items)
	if items:
		for project in items:
			frappe.db.sql(""" delete from `tabItem Reorder` where parent in (select name from `tabItem` where project='{}')  """.format(project))
			frappe.db.commit()
			
	frappe.msgprint("Reset re-order")



#sale sorder from
@frappe.whitelist()
def fetch_delivery_type(doc,method):
	so=[]
	for i in doc.items:
		if i.sales_order:
			so.append(i.sales_order)
			break
		
	if so:
		sodoc=frappe.get_doc("Sales Order",so[-1])
		doc.db_set("custom_delivery_type",sodoc.delivery_type, update_modified=False)
		doc.db_set("custom_delivery_location",sodoc.delivery_location, update_modified=False)
	

@frappe.whitelist()
def fetch_delivery_type_old():
	mr=frappe.db.sql("""select parent ,sales_order from `tabMaterial Request Item` where sales_order is not null  and parent in (select name from `tabMaterial Request` where docstatus=1 and material_request_type='Material Transfer' and status='Pending') """,as_dict=1)
	if mr:
		for i in mr:
			mr=i['parent']
			so=i['sales_order']
			print(mr)
			sodoc=frappe.get_doc("Sales Order",so)
			frappe.db.sql(""" update `tabMaterial Request` set  custom_delivery_type='{}' , custom_delivery_location='{}'   where name='{}'  """.format(sodoc.delivery_type,sodoc.delivery_location,mr))
			frappe.db.commit()
			


@frappe.whitelist()
def before_insert_set_automted(doc,method):
	check_for_automated=[]
	for i in doc.items:
		if i.production_plan:
			check_for_automated.append("yes")
			break
		
	if check_for_automated:
		doc.set("custom_is_production",1)


@frappe.whitelist()
def before_insert_set_automted_old():
	get_mr=frappe.db.sql("""select DISTINCT name from `tabMaterial Request` where  docstatus<2 and custom_is_production=0 and name in (select parent from `tabMaterial Request Item`  where production_plan is not null and docstatus<2)  """,as_dict=1)
	if get_mr:
		for m in get_mr:
			doc=frappe.get_doc("Material Request",m['name'])
			print(doc.name)
			frappe.db.sql("""update `tabMaterial Request`  set custom_is_production=1   where name='{}'  """.format(doc.name))
			frappe.db.commit()





@frappe.whitelist()
def bulk_stop_material_requests(material_requests):
    print(material_requests)
    material_requests = frappe.parse_json(material_requests)
    for name in material_requests:
        print(name)
        mr = frappe.get_doc("Material Request", name)
        print(mr)
        if mr.docstatus == 1 and mr.status != "Stopped":
            print(mr.status)
            mr.update_status("Stopped")
        # mr.save()
    return 'done'
