import frappe


@frappe.whitelist(allow_guest=True)
def make_all_kit_for_item(doc,method):
    if doc.variant_of:
        if doc.attributes:
            attrb=[]
            for i in doc.attributes:
                if i.attribute in ["Print","Handwork","Block Print"]:
                    get_abr=frappe.db.sql("""select abbr from `tabItem Attribute Value` where parent='{}' and attribute_value='{}' """.format(i.attribute,i.attribute_value),as_dict=1)
                    if len(get_abr)!=0:
                        if get_abr[0]['abbr']!=0:
                            ab=get_abr[0]['abbr']+"K"
                            make_kit_level_wise(item_name=doc.item_name,item=doc.name,item_group=doc.item_group,level=ab,image=doc.image,project=doc.project)




@frappe.whitelist(allow_guest=True)
def make_all_kit_for_item_old():
    get_items=frappe.db.sql("""select DISTINCT name from `tabItem` where variant_of is  not null and name like '16%'   """,as_dict=1)
    if get_items:
        for dc in get_items:
            print(dc['name'])
            doc=frappe.get_doc("Item",dc['name'])
            if doc.variant_of:
                if doc.attributes:
                    attrb=[]
                    for i in doc.attributes:
                        if i.attribute in ["Print","Handwork","Block Print"]:
                            get_abr=frappe.db.sql("""select abbr from `tabItem Attribute Value` where parent='{}' and attribute_value='{}' """.format(i.attribute,i.attribute_value),as_dict=1)
                            if len(get_abr)!=0:
                                if get_abr[0]['abbr']!=0:
                                    ab=get_abr[0]['abbr']+"K"
                                    make_kit_level_wise(item_name=doc.item_name,item=doc.name,item_group=doc.item_group,level=ab,image=doc.image,project=doc.project)






@frappe.whitelist(allow_guest=True)
def make_kit_level_wise(item_name=None,item=None,item_group=None,level=None,image=None,project=None):
    is_subcontract=0
    if not level:
        return


    new_kit_name=item+"-"+level
    print(new_kit_name,"56")
    if frappe.db.exists("Item",new_kit_name):
        return

    d={"doctype":"Item","item_group":"M kit","stock_uom":"Meter","image":image,"is_sub_contracted_item":0}
    if project:
        d['project']=project
    if item_name:
        d['item_name']=item_name
    d['parent_item']=item
    d['item_code']=new_kit_name
    if item_group=="Sample":
        is_subcontract=0
    if item_group=="Ready Stock":
        is_subcontract=1
    d['is_sub_contracted_item']=is_subcontract
    kit_insert=frappe.get_doc(d)
    try:
        kit_insert.insert(ignore_permissions=True)
    except:
        pass


@frappe.whitelist(allow_guest=True)
def make_kit_level_wise_old(item_name=None,item=None,item_group=None,level=None,image=None,project=None):
    is_subcontract=0
    if not level:
        return

    new_kit_name=item+"-"+level
    print(new_kit_name,"56")
    if frappe.db.exists("Item",new_kit_name):
        return

    d={"doctype":"Item","item_group":"M kit","stock_uom":"Nos","image":image}
    if project:
        d['project']=project
    if item_name:
        d['item_name']=item_name
    d['item_code']=new_kit_name
    if item_group=="Sample":
        is_subcontract=0
    if item_group=="Ready Stock":
        is_subcontract=1
    d['is_sub_contracted_item']=is_subcontract
    kit_insert=frappe.get_doc(d)
    try:
        kit_insert.insert(ignore_permissions=True)
        frappe.db.commit()
    except:
        pass




@frappe.whitelist(allow_guest=True)
def set_project_kit(doc,method):
    if doc.parent_item and not doc.project:
        if frappe.db.exists("Item",doc.parent_item):
            parent=frappe.get_doc("Item",doc.parent_item)
            if parent.project:
                doc.db_set("project",parent.project, update_modified=False)


@frappe.whitelist(allow_guest=True)
def set_project_by(doc,method):
    if doc.name:
        name=doc.name
        split=name.split("-")
        project="PROJ-"+str(split[0])
        if frappe.db.exists("Project",project):
            doc.db_set("project",project, update_modified=False)



@frappe.whitelist(allow_guest=True)
def set_project_bys():
    #get_items=frappe.db.sql("""select name from `tabItem` where name like '%-BPK' """,as_dict=1)
    #get_items=frappe.db.sql("""select name from `tabItem` where name like '%-HEK' """,as_dict=1)
    get_items=frappe.db.sql("""select name from `tabItem` where name like '%-DPK' """,as_dict=1)
    if get_items:
        for i in get_items:
            if frappe.db.exists("Item",i['name']):
                print(i['name'],"hi")
                doc=frappe.get_doc("Item",i['name'])
                name=doc.name
                split=name.split("-")
                project="PROJ-"+str(split[0])
                if frappe.db.exists("Project",project):
                    doc.db_set("project",project, update_modified=False)
                
                try:
                    doc.save()
                    frappe.db.commit()
                except:
                    pass

    
