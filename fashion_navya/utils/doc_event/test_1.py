import frappe

@frappe.whitelist()
def bom_rpl_disabled():
	get_bom=[]
	items_disabled=[]
	temp=[]
	sample=[]
	sbom=[]
	tbom=[]
	notbom=[]
	notitem=[]
	finds=frappe.db.sql("""select  parent from `tabBOM Item` where docstatus=1 and item_code in (select name from `tabItem` where disabled=1)  """,as_dict=1)
	for i in finds:
		get_bom.append(i['parent'])

	boms=list(set(get_bom))
	for i in boms:
		if frappe.db.exists("BOM",i):
			bom=frappe.get_doc("BOM",i)
			if frappe.db.exists("Item",bom.item):
				item=frappe.get_doc("Item",bom.item)
				if item.has_variants==1:
					temp.append(item.name)
					tbom.append(bom.name)
				if item.item_group=="Sample" and item.variant_of:
					sample.append(item.name)
					sbom.append(bom.name)
				if item.disabled==1:
					items_disabled.append(item.name)
			else:
				notitem.append(bom.item)
		else:
			notbom.append(i)


	dis=list(set(items_disabled))
	smplbom=list(set(sbom))
	tempbom=list(set(tbom))
	print(dis,'items_disabled',len(dis))
	#print(temp,"temp item",len(temp))
	#print(sample,"sample item",len(sample))
	print(sbom,"sample bom",len(smplbom))
	print(tbom,'tem bom',len(tempbom))







@frappe.whitelist()
def old_customer():
	get_mr=frappe.db.sql("""select * from `tabMaterial Request Item` where sales_order is not null and docstatus=1  """,as_dict=1)
	if get_mr:
		for i in get_mr:
			print(i['parent'])
			if i['sales_order']:
				so=frappe.get_doc("Sales Order",i['sales_order'])
				get_wo=frappe.db.sql("""select name from `tabWork Order` where docstatus<2 and material_request='{}'  """.format(i['parent']),as_dict=1)
				if get_wo:
					frappe.db.sql("""update `tabWork Order` set sales_order='{}' where name='{}'  """.format(so.name,get_wo[0]['name']))
				frappe.db.sql("""update `tabMaterial Request` set custom_customer='{}' where name='{}'  """.format(so.customer,i['parent']))
				frappe.db.sql("""update `tabMaterial Request Item` set custom_customer='{}' where  parent='{}'  """.format(so.customer,i['parent']))
				frappe.db.commit()



def update_del_date_so():
	get_so=frappe.db.sql("""select  DISTINCT sales_order from `tabMaterial Request Item` where sales_order is not null  and docstatus < 2 """,as_dict=1)
	if get_so:
		for so in get_so:
			print(so['sales_order'])
			doc=frappe.get_doc("Sales Order",so['sales_order'])
			for i in doc.items:
				get_mr=frappe.db.sql("""select parent from  `tabMaterial Request Item` where item_code='{}' and sales_order='{}'  """.format(i.item_code,doc.name),as_dict=1)
				if get_mr:
					mr_list=[]
					for k in get_mr:
						if k['parent'] not in mr_list:
							frappe.db.sql("""update `tabMaterial Request` set custom_delivery_date='{}' where name='{}'  """.format(i.delivery_date,k['parent']))
							mr_list.append(k['parent'])


				#print(k['parent'],'1')
				frappe.db.sql("""update `tabMaterial Request Item` set custom_delivery_date='{}' where item_code='{}' and sales_order='{}'  """.format(i.delivery_date,i.item_code,doc.name))
				frappe.db.commit()
				frappe.db.sql("""update `tabWork Order` set expected_delivery_date='{}' where sales_order='{}' and production_item='{}'  """.format(doc.delivery_date,doc.name,i.item_code))
				frappe.db.commit()


@frappe.whitelist()
def delete_temp():
	get_all=frappe.db.sql("""select name from `tabProject Template`  """,as_dict=1)
	for i in get_all:
		if frappe.db.exists("Project Template",i['name']):
			doc=frappe.get_doc("Project Template",i['name'])
			project=frappe.db.sql("""select name from `tabProject` where project_template='{}' """.format(doc.name),as_dict=1)
			if len(project)==0:
				try:
					doc.delete()
					frappe.db.commit()
					print(doc.name)
				except:
					continue
			
	new_update=['TASK-2024-00190',"TASK-2024-00189",'TASK-2024-00188','TASK-2024-00187','TASK-2024-00186','TASK-2024-00185']
	for i in get_all:
		if frappe.db.exists("Project Template",i['name']):
			docs=frappe.get_doc("Project Template",i["name"])
			for j in new_update:
				row = docs.append("tasks", {})
				row.task=j
			docs.save()
			frappe.db.commit()



@frappe.whitelist()
def add_sizes():
	l=["Extra Small","Small","Medium","Large","Extra Large","Double XL","Triple XL"]
	get_sil=frappe.db.sql("""select name from `tabSilhouette`   """,as_dict=1)
	if get_sil:
		for i in get_sil:
			doc=frappe.get_doc("Silhouette",i['name'])
			m=[]
			if not doc.ready:
				for j in l:
					row=doc.append("ready", {})
					row.sizes=j
					m.append("3")
			if not doc.capacity__silhouette:
				for k in l:
					row1=doc.append("capacity__silhouette", {})
					row1.sizes=k
					m.append("9")
					print(k)
					
			doc.save()
			frappe.db.commit()