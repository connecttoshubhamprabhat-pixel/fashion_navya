import frappe
from erpnext.stock.dashboard.item_dashboard import get_data
from datetime import datetime
from frappe.utils import add_to_date
from fashion_navya.utils.doc_event.item import make_kit_item
from navya.api_folder.py.project import (make_pattren_from_variant_so,bom_copy_so_enabled_item
        ,bom_copy_so_enabled_submit,bom_copy_so_draft)
import json
import re
from fashion_navya.utils.doc_event.item import make_kit_item
from navya.api_folder.py.item_variants import create_multiple_variants_custom,create_variant_custom
from erpnext.controllers.item_variant import (
	ItemVariantExistsError,
	copy_attributes_to_variant,
	get_variant,
	make_variant_item_code,
	validate_item_variant_attributes,
)


@frappe.whitelist(allow_guest=True)
def set_price(item_code=None):
    if item_code!=None:
        rate=frappe.db.sql("""select price_list_rate from `tabItem Price` where workflow_state="Approved" and item_code='{}' ORDER BY modified DESC   """.format(item_code),as_dict=1)
        if len(rate)!=0:
            return  rate[0]['price_list_rate']
        else:
            return 0


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



@frappe.whitelist(allow_guest=True)
def make_ptt_so(old=None,new=None):
    get_ptt=frappe.db.sql("""select name from `tabPattern` where docstatus=1 and item_code='{}'  """.format(old),as_dict=1)
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
def create_item_customer(items=None,values=None,so=None,customer=None):
    if not customer:
        frappe.throw("Please select customer")
    items=json.loads(items)
    #frappe.throw("aa")
    values=json.loads(values)
    size_get=values.get("size")
    type_get=values.get("type")

    if type_get=="Customise":
        print(78)
        item=make_rtw_item_so(items=items,so=so,size=size_get,type=type_get)
        data=[]
        data.append(item)
        data.append("Customise")
        return data
    if type_get=="RTW":
        item=make_rtw_item_so(items=items,so=so,size=size_get,type=type_get)
        data=[]
        data.append(item)
        data.append("RTW")
        return data
    if type_get=="MTM":
        item=make_MTM_item(items=items,so=so,size=size_get,customer=customer,type=type_get)
        data=[]
        data.append(item)
        data.append("MTM")
        return data




@frappe.whitelist()
def make_customer_items(items=None,so=None,size=None,customer=None):
    all_item=[]
    get_all_sizes=[]
    val=frappe.db.sql("""select abbr from `tabItem Attribute Value` where parent="Size"  """,as_dict=1)
    if val:
        for v in val:
            get_all_sizes.append(v['abbr'])

    for i in items:
        parent_doc=frappe.get_doc("Item",i)
        if not parent_doc.variant_of:
            return
        #get price_list
        price=set_price(item_code=i)
        perdoc=frappe.get_doc("Permitted Files","PFL-2023-00008")
        if int(perdoc.cms)>int(price):
            frappe.msgprint("The Price is less then 10000")
            return

        split_parent=i.split("-")
        submit=0
        if size in split_parent:
            submit=1
        #remove HTML tag
        CLEANR = re.compile('<.*?>')
        des= re.sub(CLEANR, '',parent_doc.description)

        for s in get_all_sizes:
            if s in split_parent:
                index =split_parent.index(s)
                split_parent[index]=size

        for ss in split_parent:
            if "SMPL"==ss:
                split_parent.remove(ss)
        if "RTW" not in split_parent:
            split_parent.append("RTW")


        final_name="-".join(split_parent)
        print(final_name,"name")
        if frappe.db.exists("Item",final_name):
            item_doc_exists=frappe.get_doc("Item",final_name)
            if not item_doc_exists.variant_of:
                return final_name
        print(final_name,"names")
        bom=bom_fetched(parent=parent_doc.name,size=size)
        d={'doctype':"Item","item_group":"Customise","project":parent_doc.project ,"stock_uom":parent_doc.stock_uom,"image":parent_doc.image}
        d['item_code']=final_name
        d['item_name']=final_name
        d['parent_item']=parent_doc.name
        d['customise']=1
        d['description']=des
        n=frappe.get_doc(d)
        row =n.append("customer_list", {})
        row.customer=customer
        n.save(ignore_permissions=True)
        n.db_set("description",des, update_modified=False)
        make_kit_item(name=n.name)
        make_price_doc(item=n.name,rate=price)
        make_bom(new=n.name,submit=submit,variant=0,bom=bom)
        all_item.append(n.name)

    if all_item:
        return all_item[-1]


@frappe.whitelist()
def make_MTM_item(items=None,so=None,size=None,customer=None,type=None):
    if not customer:
        frappe.msgprint("Please Select Customer")
        return

    cs=customer.split(" ")
    customer_count=[]
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

    all_item=[]
    get_all_sizes=[]
    val=frappe.db.sql("""select abbr from `tabItem Attribute Value` where parent="Size"  """,as_dict=1)
    if val:
        for v in val:
            get_all_sizes.append(v['abbr'])

    for i in items:
        parent_doc=frappe.get_doc("Item",i)
        digital=[]
        if not parent_doc.variant_of:
            print(198)
            return
        #check for digital
        for ap in parent_doc.attributes:
            if ap.attribute_value=="Digital":
                digital.append("a")
        if digital:
            frappe.msgprint("This is Digital print Item")
            return
        #get price_list
        price=set_price(item_code=i)
        perdoc=frappe.get_doc("Permitted Files","PFL-2023-00008")
        if int(perdoc.mtm)>int(price):
            frappe.msgprint("The Price is less then 10000")
            return



        split_parent=i.split("-")
        #remove HTML tag
        CLEANR = re.compile('<.*?>')
        des= re.sub(CLEANR, '',parent_doc.description)
        submit=0
        if size in split_parent:
            submit=1

        for s in get_all_sizes:
            if s in split_parent:
                index =split_parent.index(s)
                split_parent[index]=size

        for ss in split_parent:
            if "SMPL"==ss:
                split_parent.remove(ss)

        final_name="-".join(split_parent)
        name_set=final_name+"-"+"MTM"
        cus_name=final_name+"-"+"MTM"+"-"+customer_count[0]
        print(cus_name,"name")
        if frappe.db.exists("Item",cus_name):
            print(229)
            return cus_name
        print(cus_name,"names")

        bom=bom_fetched(parent=parent_doc.name,size=size)


        name_item_rename=item_remame(name=parent_doc.item_name)
        d={'doctype':"Item","item_group":"Customise","project":parent_doc.project ,"stock_uom":parent_doc.stock_uom,"image":parent_doc.image}
        d['item_code']=cus_name
        d['item_name']=name_item_rename+"-"+"MTM"+"-"+customer
        d['parent_item']=parent_doc.name
        d['customise']=1
        d['description']=des
        n=frappe.get_doc(d)
        row =n.append("customer_list", {})
        row.customer=customer
        n.save(ignore_permissions=True)
        n_name_new=name_set+"-"+customer
        n.db_set("description",des, update_modified=False)
        #n.db_set("item_name",n_name_new, update_modified=False)
        make_kit_item(name=n.name)
        make_price_doc(item=n.name,rate=price)
        all_item.append(n.name)
        make_bom(new=n.name,submit=0,variant=0,bom=bom)
        make_ptt_so(old=parent_doc.name,new=n.name)



    if all_item:
        return all_item[-1]




#sales ordr-sales order
@frappe.whitelist(allow_guest=True)
def make_rtw_item_so(items=None,so=None,size=None,type=None):
    if not items and not size:
        return

    get_all_sizes=[]
    val=frappe.db.sql("""select abbr from `tabItem Attribute Value` where parent="Size"  """,as_dict=1)
    if val:
        for v in val:
            get_all_sizes.append(v['abbr'])

    items_list=items
    for m in items_list:
        price=set_price(item_code=m)
        perdoc=frappe.get_doc("Permitted Files","PFL-2023-00008")
        if type=="Customise":
            if int(perdoc.cms)>int(price):
                frappe.msgprint("The Price is less then 10000")
                return

        item_doc=frappe.get_doc("Item",m)
        if item_doc.item_group!="Sample":
            frappe.msgprint("Please Select Sample")
            return

        split_name=item_doc.name.split("-")
        submit=0
        get_bom_name=bom_fetched(parent=item_doc.name,size=size) or None
        if size in split_name:
            submit=1
            if "SMPL" in split_name:
                index =split_name.index("SMPL")
                split_name[index]="RTW"
                name_rtw="-".join(split_name)
                print(name_rtw,"aa")
                if frappe.db.exists("Item",name_rtw):
                    get_bom=frappe.db.sql("""select name from `tabBOM` where docstatus <2 and item='{}'  """.format(name_rtw),as_dict=1)
                    if len(get_bom)==0:
                        make_bom(new=name_rtw,submit=submit,variant=1,bom=get_bom_name)
                    return name_rtw

        get_name_of_abr=frappe.db.sql("""select attribute_value from `tabItem Attribute Value` where parent="Size" and abbr='{}' """.format(size),as_dict=1)
        if not get_name_of_abr:
            frappe.msgprint("Size is not found")
            return

        d={}
        #check for digital

        digital=[]
        if type=="Customise":
            for ap in item_doc.attributes:
                if ap.attribute_value=="Digital":
                    digital.append("a")

            #if digital:
             #   frappe.msgprint("This is Digital print Item")
              #  return

        #print("276")
        for m in item_doc.attributes:
            if m.attribute!="Item Group":
                d[m.attribute]=m.attribute_value

        d['Size']=get_name_of_abr[0]['attribute_value']
        print()
        d['Item Group']="Ready To Wear"
        print("282",d)
        print(size,'size')
        get_exists=get_variant(item_doc.variant_of, d)
        if get_exists:
            get_bom=frappe.db.sql("""select name from `tabBOM` where docstatus <2 and item='{}'  """.format(get_exists),as_dict=1)
            if len(get_bom)==0:
                make_bom(new=get_exists,submit=submit,variant=1,bom=get_bom_name)
            return get_exists

        variants=create_variant_custom(item_doc.variant_of,d)
        if item_doc.project:
            variants.set("project",item_doc.project)

        if item_doc.image:
            variants.set("image",item_doc.image)

        print("291")
        variants.set("item_group","Ready Stock")
        check_item=frappe.db.sql("""select name from `tabItem` where item_code='{}'  """.format(variants.item_code),as_dict=1)
        if len(check_item)!=0:
            if frappe.db.exists("Item",check_item[0]['name']):
                get_bom=frappe.db.sql("""select name from `tabBOM` where docstatus <2 and item='{}'  """.format(check_item[0]['name']),as_dict=1)
                if len(get_bom)==0:
                    make_bom(new=check_item[0]['name'],submit=submit,variant=1,bom=get_bom_name)
                return check_item[0]['name']

        variants.save(ignore_permissions=True)
        if variants:
            make_ptt_so(old=item_doc.name,new=variants.name)
            make_bom(new=variants.name,submit=submit,variant=1,bom=get_bom_name)
            return variants.name


#sales ordr-sales order
@frappe.whitelist(allow_guest=True)
def get_size_name(name=None,abbr=None):
    if abbr:
        get_name_of_name=frappe.db.sql("""select attribute_value from `tabItem Attribute Value` where parent="Size" and abbr='{}' """.format(abbr),as_dict=1)
        if get_name_of_name:
            return get_name_of_name[0]['attribute_value']
    if name:
        get_name_of_abr=frappe.db.sql("""select abbr from `tabItem Attribute Value` where parent="Size" and attribute_value='{}' """.format(name),as_dict=1)
        if get_name_of_abr:
            return get_name_of_abr[0]['abbr']

@frappe.whitelist(allow_guest=True)
def get_exists_with_same_att(template=None,att=None):
    get_exists=get_variant(template,att)
    if get_exists:
        return get_exists


@frappe.whitelist(allow_guest=True)
def make_bom(new=None,submit=0,variant=0,bom=None):
    if bom and new:
        bm=frappe.get_doc("BOM",bom)
        d=frappe.copy_doc(bm)
        d.set("item",new)
        if bm.pattern_not_required==1:
            d.set('pattern_not_required',1)
        d.set("workflow_state","Draft")
        if variant==1:
            for raw in d.items:
                split=raw.item_code.split("-")
                new_parent_split=new.split("-")
                if raw.idx==1:
                    kit_new=new+"-k"
                    if frappe.db.exists("Item",kit_new):
                        raw.set("item_code",kit_new)
                        raw.set("bom_no",None)
        try:
            d.insert(ignore_permissions=True)
            if submit==1:
                d.submit()
        except:
            pass


@frappe.whitelist(allow_guest=True)
def get_abbr_from_size(parent=None):
    doc=frappe.get_doc("Item",parent)
    size=[]
    for i in doc.attributes:
        if i.attribute=="Size":
            size.append(i.attribute_value)
    if size:
        name=get_size_name(name=size[0])
        return name

@frappe.whitelist(allow_guest=True)
def bom_fetched(parent=None,size=None):
    doc=frappe.get_doc("Item",parent)
    get_abr=get_abbr_from_size(parent=doc.name)
    split_name=doc.name.split("-")
    if get_abr:
        for abr_name in split_name:
            if abr_name==get_abr:
                index =split_name.index(abr_name)
                split_name[index]=size

    #check same size attributes exists
    name_new_size="-".join(split_name)
    bom_list=[]
    if frappe.db.exists("Item",name_new_size):
        get_bom=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and is_active=1 and is_default=1 and item='{}' """.format(name_new_size),as_dict=1)
        if len(get_bom)!=0:
            bom_list.append(get_bom[0]['name'])
    else:
        get_bom_parent=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and is_active=1 and is_default=1 and item='{}' """.format(doc.name),as_dict=1)
        if len(get_bom_parent)!=0:
            bom_list.append(get_bom_parent[0]['name'])
        else:
            variant_of_bom=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and item in (select name from `tabItem` where variant_of='{}')  """.format(doc.variant_of),as_dict=1)
            if variant_of_bom:
                bom_list.append(variant_of_bom[0]['name'])
            else:
                variant_of_bom=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and item='{}' """.format(doc.variant_of),as_dict=1)
                if variant_of_bom:
                    bom_list.append(variant_of_bom[0]['name'])



    if bom_list:
        return bom_list[-1]






#kit bom copy
@frappe.whitelist(allow_guest=True)
def make_bom_kit_new(doc,method):
    if not doc.variant_of and doc.item_group=="M kit":
        #frappe.throw("aaaaaa")
        split_parent=doc.name.split("-")
        get_parent=split_parent[:-1]
        join_parent="-".join(get_parent)
        print(join_parent,'join_parent')
        if frappe.db.exists("Item",join_parent):
            #print("468")
            item_doc=frappe.get_doc("Item",join_parent)
            if item_doc.variant_of:
                #print("471")
                item_doc_parent=item_doc.name.split("-")
                if "RTW" in item_doc_parent:
                    index=item_doc_parent.index("RTW")
                    item_doc_parent[index]="SMPL"

                join_smpl="-".join(item_doc_parent)
                get_bom_smpl=frappe.db.sql(""" select name from `tabBOM` where docstatus=1 and item='{}' """.format(join_smpl),as_dict=1)
                get_bom_kit=frappe.db.sql(""" select name from `tabBOM` where docstatus=1 and item='{}' """.format(doc.name),as_dict=1)
                if not get_bom_kit and get_bom_smpl:
                    if doc.has_variants==0 and not doc.variant_of and doc.item_group=="M kit":
                        bm=frappe.get_doc("BOM",get_bom_smpl[0]['name'])
                        d=frappe.copy_doc(bm)
                        d.set("item",doc.name)
                        d.set('pattern_not_required',1)
                        d.set("workflow_state","Draft")
                        try:
                            d.insert(ignore_permissions=True)
                            d.submit()
                        except:
                            pass
            else:
                if item_doc.parent_item:
                    #print("490")
                    item_doc_parent=item_doc.parent_item.split("-")
                    if "RTW" in item_doc_parent:
                        index=item_doc_parent.index("RTW")
                        item_doc_parent[index]="SMPL"

                    join_smpl="-".join(item_doc_parent)
                    get_bom_smpl=frappe.db.sql(""" select name from `tabBOM` where docstatus=1 and item='{}' """.format(join_smpl),as_dict=1)
                    get_bom_kit=frappe.db.sql(""" select name from `tabBOM` where docstatus=1 and item='{}' """.format(doc.name),as_dict=1)
                    if not get_bom_kit and get_bom_smpl:
                        print("5000")
                        if doc.has_variants==0 and not doc.variant_of and doc.item_group=="M kit":
                            #print("502")
                            bm=frappe.get_doc("BOM",get_bom_smpl[0]['name'])
                            d=frappe.copy_doc(bm)
                            d.set("item",doc.name)
                            d.set('pattern_not_required',1)
                            d.set("workflow_state","Draft")
                            try:
                                d.insert(ignore_permissions=True)
                                d.submit()
                            except:
                                pass




#kit bom copy
@frappe.whitelist(allow_guest=True)
def make_bom_kit_new_manual(name=None):
    if not name:
        return
    doc=frappe.get_doc("Item",name)
    if not doc.variant_of and doc.item_group=="M kit":
        #frappe.throw("aaaaaa")
        split_parent=doc.name.split("-")
        get_parent=split_parent[:-1]
        join_parent="-".join(get_parent)
        print(join_parent,'join_parent')
        if frappe.db.exists("Item",join_parent):
            #print("468")
            item_doc=frappe.get_doc("Item",join_parent)
            if item_doc.variant_of:
                #print("471")
                item_doc_parent=item_doc.name.split("-")
                if "RTW" in item_doc_parent:
                    index=item_doc_parent.index("RTW")
                    item_doc_parent[index]="SMPL"

                join_smpl="-".join(item_doc_parent)
                get_bom_smpl=frappe.db.sql(""" select name from `tabBOM` where docstatus=1 and item='{}' """.format(join_smpl),as_dict=1)
                get_bom_kit=frappe.db.sql(""" select name from `tabBOM` where docstatus=1 and item='{}' """.format(doc.name),as_dict=1)
                if not get_bom_kit and get_bom_smpl:
                    if doc.has_variants==0 and not doc.variant_of and doc.item_group=="M kit":
                        bm=frappe.get_doc("BOM",get_bom_smpl[0]['name'])
                        d=frappe.copy_doc(bm)
                        d.set("item",doc.name)
                        d.set('pattern_not_required',1)
                        d.set("workflow_state","Draft")
                        try:
                            d.insert(ignore_permissions=True)
                            d.submit()
                        except:
                            pass
            else:
                if item_doc.parent_item:
                    #print("490")
                    item_doc_parent=item_doc.parent_item.split("-")
                    if "RTW" in item_doc_parent:
                        index=item_doc_parent.index("RTW")
                        item_doc_parent[index]="SMPL"

                    join_smpl="-".join(item_doc_parent)
                    get_bom_smpl=frappe.db.sql(""" select name from `tabBOM` where docstatus=1 and item='{}' """.format(join_smpl),as_dict=1)
                    get_bom_kit=frappe.db.sql(""" select name from `tabBOM` where docstatus=1 and item='{}' """.format(doc.name),as_dict=1)
                    if not get_bom_kit and get_bom_smpl:
                        print("5000")
                        if doc.has_variants==0 and not doc.variant_of and doc.item_group=="M kit":
                            #print("502")
                            bm=frappe.get_doc("BOM",get_bom_smpl[0]['name'])
                            d=frappe.copy_doc(bm)
                            d.set("item",doc.name)
                            d.set('pattern_not_required',1)
                            d.set("workflow_state","Draft")
                            try:
                                d.insert(ignore_permissions=True)
                                d.submit()
                            except:
                                pass



@frappe.whitelist(allow_guest=True)
def item_remame(name=None):
    if name:
        res =" ".join(re.findall("[a-zA-Z]+", name))
        split_res=res.split(" ")
        new_str_list=[]
        for i in split_res:
            str_i=str(i)
            if len(str_i)>2 and not str_i.isupper() and str_i not in new_str_list:
                new_str_list.append(str_i)
        join_final_name=" ".join(new_str_list)
        if join_final_name:
            return join_final_name
        else:
            return " .."
