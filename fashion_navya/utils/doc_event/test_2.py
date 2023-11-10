import frappe
from erpnext.controllers.item_variant import (
	ItemVariantExistsError,
	copy_attributes_to_variant,
	get_variant,
	make_variant_item_code,
	validate_item_variant_attributes,
)


@frappe.whitelist(allow_guest=True)
def old_image_smpl():
	get_smpl=frappe.db.sql("""select * from `tabItem` where item_group="Sample" and  variant_of is not null and  image is not null and disabled=0  """,as_dict=1)
	if get_smpl:
		for i in get_smpl:
			print(i['name'])
			doc=frappe.get_doc("Item",i['name'])
			template=i['variant_of']
			attributes={}
			for m in doc.attributes:
				if m.attribute not in ["Item Group","Size"]:
					attributes[m.attribute]=m.attribute_value

			get_exists=get_variant(template,attributes)
			print(get_exists,"get_exists")



#fetch with same size of attributes
@frappe.whitelist()
def images_same_attributes():
	get_smpl=frappe.db.sql("""select * from `tabItem` where project='PROJ-1593'  and variant_of is not null and  image is not null and disabled=0  """,as_dict=1)
	if len(get_smpl)!=0:
		for y in get_smpl:
			name=y['name']
			image=y['image']
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
					frappe.db.commit()




