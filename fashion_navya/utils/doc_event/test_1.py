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
