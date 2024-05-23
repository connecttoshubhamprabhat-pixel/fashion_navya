import frappe
import json
import re
from bs4 import BeautifulSoup

@frappe.whitelist()
def get_urls_elements(docname):
    sites="https://erp.navyacustom.com/"
    doc=frappe.get_doc("Design Elements",docname)
    img_dup=[]
    images_list=[]
    for i in doc.elements:
        if i.pattern_attachment not in img_dup:
            img=sites+i.pattern_attachment
            d={"image_url":img}
            images_list.append(d)
            img_dup.append(i.pattern_attachment)
            
            
    get_drw_img=frappe.db.sql(""" select file_url  from   `tabFile`  where attached_to_doctype='Drawing' and attached_to_name='{}' and attached_to_field='drawing_image'  """.format(doc.drawing),as_dict=1)
    if len(get_drw_img)!=0:
        d1={}
        d1['image_url']=sites+get_drw_img[0]['file_url']
        images_list.append(d1)
        
    return images_list




@frappe.whitelist()
def get_urls_elements_drawings(docname):
    sites="https://erp.navyacustom.com/"
    doc=frappe.get_doc("Drawing",docname)
    img_dup=[]
    images_list=[]
    for i in doc.drawings:
        if i.drawing_attachment not in img_dup:
            img=sites+i.drawing_attachment
            d={"image_url":img}
            images_list.append(d)
            img_dup.append(i.drawing_attachment)
            
    return images_list



@frappe.whitelist()
def get_urls_elements_mood(docname):
    sites="https://erp.navyacustom.com/"
    doc=frappe.get_doc("Mood Board",docname)
    img_dup=[]
    images_list=[]
    for i in doc.drawings:
        if i.drawing_attachment:
            if i.drawing_attachment not in img_dup:
                img=sites+i.drawing_attachment
                d={"image_url":img}
                images_list.append(d)
                img_dup.append(i.drawing_attachment)
                
    return images_list



@frappe.whitelist()
def get_urls_elements_events(docname):
    sites="https://erp.navyacustom.com/"
    doc=frappe.get_doc("Events",docname)
    img_dup=[]
    images_list=[]
    for i in doc.event_item:
        if i.image not in img_dup and i.image!=None:
            img=sites+i.image
            d={"image_url":img}
            images_list.append(d)
            img_dup.append(i.image)
            
    for i in doc.event_items:
        if i.image not in img_dup and i.image!=None:
            img=sites+i.image
            d={"image_url":img}
            images_list.append(d)
            img_dup.append(i.image)
    
    for i in doc.events_product:
        if i.image not in img_dup and i.image!=None:
            img=sites+i.image
            d={"image_url":img}
            images_list.append(d)
            img_dup.append(i.image)
    
    
            
    return images_list





@frappe.whitelist()
def get_urls_elements_events_ready(docname):
    sites="https://erp.navyacustom.com/"
    doc=frappe.get_doc("Events",docname)
    img_dup=[]
    images_list=[]
    for i in doc.event_items:
        if i.image not in img_dup and i.image!=None:
            img=sites+i.image
            d={"image_url":img}
            images_list.append(d)
            img_dup.append(i.image)
            
    return images_list




@frappe.whitelist()
def get_urls_elements_events_sample(docname):
    sites="https://erp.navyacustom.com/"
    doc=frappe.get_doc("Events",docname)
    img_dup=[]
    images_list=[]
    
    
    for i in doc.event_item:
        if i.image not in img_dup and i.image!=None:
            img=sites+i.image
            d={"image_url":img}
            images_list.append(d)
            img_dup.append(i.image)
            
    return images_list



@frappe.whitelist()
def get_urls_elements_events_display(docname):
    sites="https://erp.navyacustom.com/"
    doc=frappe.get_doc("Events",docname)
    img_dup=[]
    images_list=[]
    
    
    for i in doc.events_product:
        if i.image not in img_dup and i.image!=None:
            img=sites+i.image
            d={"image_url":img}
            images_list.append(d)
            img_dup.append(i.image)
            
    return images_list


@frappe.whitelist()
def get_urls_elements_pattern(docname):
    sites="https://erp.navyacustom.com"
    doc=frappe.get_doc("Pattern",docname)
    img_dup=[]
    images_list=[]
    if doc.sheet_no!=8:
        get_pattern_img=frappe.db.sql(""" select file_url  from   `tabFile`  where attached_to_doctype='Pattern' and attached_to_name='{}' and attached_to_field='file'  """.format(doc.name),as_dict=1)
        if len(get_pattern_img)!=0:
            d={}
            d['image_url']=sites+get_pattern_img[0]['file_url']
            images_list.append(d)
            
            
            
            
        get_drw_img=frappe.db.sql(""" select file_url  from   `tabFile`  where attached_to_doctype='Drawing' and attached_to_name='{}' and attached_to_field='drawing_image'  """.format(doc.drawing),as_dict=1)
        if len(get_drw_img)!=0:
            d1={}
            d1['image_url']=sites+get_drw_img[0]['file_url']
            images_list.append(d1)
            
            
            
        get_smpl_img=frappe.db.sql(""" select file_url  from   `tabFile`  where attached_to_doctype='Sample' and attached_to_name='{}' and attached_to_field='file'  """.format(doc.sample),as_dict=1)
        if len(get_smpl_img)!=0:
            d2={}
            d2['image_url']=sites+get_smpl_img[0]['file_url']
            images_list.append(d2)


    else:
        frappe.msgprint("Only for SHeet no:-4")
        
        
        
    return images_list





@frappe.whitelist()
def make_pur_est(items=None):
    items=json.loads(items)
    if items:
        d={"doctype":"Purchase Estimate"}
        doc=frappe.get_doc(d)
        for i in items:
            name=i.get('name')
            mr=frappe.get_doc("Material Request",name)
            for j in mr.items:
                row=doc.append("estimate_sheet_item_price", {})
                row.item_code=j.item_code
                row.qty=j.qty
                row.required_date=j.schedule_date
        
        doc.insert()
        frappe.msgprint("Created")


@frappe.whitelist()
def notification_todo(values=None,name=None,doctype=None):
    values=json.loads(values)
    description=values.get('msg')
    assigned_to=values.get("user")
    subject="It's urgent. Please."
    msg_publish="{}-{},,{}".format(doctype,name,description)
    msg_publish=get_message(doctype=doctype,name=name,send=frappe.session.user,msg=description)
    todo = frappe.get_doc({
        "doctype": "ToDo",
        "description": description,
        "status": "Open",
        "reference_type":doctype,
        "reference_name":name,
        "allocated_to":assigned_to,
        "assigned_by":frappe.session.user,
        "priority": "Medium",  # You can adjust priority as needed
        "subject": subject
    })
    todo.insert(ignore_permissions=True)  # Ignore permissions for simplicity
    frappe.msgprint("Sent")
    frappe.publish_realtime(event="msgprint", message=msg_publish, user=assigned_to)



@frappe.whitelist()
def real_time_notification_todo(values=None,name=None,doctype=None):
    values=json.loads(values)
    message=values.get('msg')
    user=values.get("user")
    msg="{}-{},,{}".format(doctype,name,message)
    frappe.publish_realtime(event="msgprint", message=msg, user=user)
    #frappe.db.commit()


@frappe.whitelist()
def real_time_msg(doc,method):
    email_pattern = r'([\w\.-]+)@([\w\.-]+)'
    if doc.content:
        matches = re.findall(email_pattern, doc.content)
        soup = BeautifulSoup(doc.content, 'html.parser')
        text_without_html = soup.get_text()
        split=text_without_html.split('\xa0')
        cmsg=split[-1]
        if doc.comment_type in ['Assigned','Comment']:
            if matches:
                email = matches[0][0] + "@" + matches[0][1]
                msg="{}-{} ,,,-{}".format(doc.reference_doctype,doc.reference_name,cmsg)
                msg=get_message(doctype=doc.reference_doctype,name=doc.reference_name,send=doc.owner,msg=cmsg)
                frappe.publish_realtime(event="msgprint", message=msg, user=email)

@frappe.whitelist()
def real_time_msg_todo(doc,method):
    msg="{}-{} ,,,-{}".format(doc.reference_type,doc.reference_name,doc.description)
    msg=get_message(doctype=doc.reference_type,name=doc.reference_name,send=doc.owner,msg=doc.description)
    frappe.publish_realtime(event="msgprint", message=msg, user=doc.allocated_to)



@frappe.whitelist()
def get_message(doctype=None,name=None,send=None,msg=None):
    doc=doctype.lower()
    split_doc=doc.split(" ")
    join_doc="-".join(split_doc)
    return 'Assigned by:-({}) <a href="https://erp.navyacustom.com/app/{}/{}" onclick="location.reload()">{}</a>:{}'.format(send,join_doc,name,doctype,msg)



@frappe.whitelist()
def set_update_stock(name=None,location=None):
    if not location:
        frappe.throw("Location is missing")
        
    doc=frappe.get_doc("Physical Stock Count", name)
    get_child_warehouse=[]
    parent_Warehouse=[]
    if location in "Santushti":
        parent_Warehouse.append("Santushti - NAVYA")
        
    if location in "Pune":
        parent_Warehouse.append("Pune - NAVYA")
        
    if location in "Sainik Farm":
        parent_Warehouse.append("Sainik Farm - NAVYA")
        
    if parent_Warehouse:
        get_w=frappe.db.sql("""select name from `tabWarehouse`  where parent_warehouse='{}' and disabled=0   """.format(parent_Warehouse[-1]),as_dict=1)
        for q in get_w:
            get_child_warehouse.append(q['name'])
    
    set_warehouses=list(set(get_child_warehouse))
    save_true=[]
    if set_warehouses:
        for i in doc.items:
            qty_all=[0]
            item=i.item_code
            for w in set_warehouses:
                balance_qty = frappe.db.sql("""select qty_after_transaction from `tabStock Ledger Entry` where item_code=%s and warehouse=%s and is_cancelled='No'   order by posting_date desc, posting_time desc, name desc  limit 1 """,(item,w),as_dict=1)
                if len(balance_qty)!=0:
                    save_true.append("aa")
                    qty_all.append(balance_qty[0]['qty_after_transaction'])
                    
            i.set("aqty",0)
            i.set("aqty",sum(qty_all))
    
    if save_true:
        doc.save()
        frappe.msgprint("Updated")


    
    
    
        

@frappe.whitelist()
def make_delement_el(doc,method):
    itemdoc=frappe.get_doc("Item",doc.item_code)
    if itemdoc.has_variants:
        items=frappe.db.sql("""select DISTINCT name from `tabItem` where variant_of='{}'  """.format(doc.item_code),as_dict=1)
        if len(items)!=0:
            for i in items:
                d_doc=frappe.get_doc("Design Elements",doc.name)
                dp=frappe.copy_doc(d_doc)
                dp.set("item_code",i['name'])
                dp.set("docstatus",0)
                dp.set("workflow_state","Draft")
                dp.insert()
                dp.submit()



@frappe.whitelist()
def make_delement_el_old(name=None):
    doc=frappe.get_doc("Design Elements",name)
    itemdoc=frappe.get_doc("Item",doc.item_code)
    if itemdoc.has_variants:
        items=frappe.db.sql("""select DISTINCT name from `tabItem` where variant_of='{}'  """.format(doc.item_code),as_dict=1)
        if len(items)!=0:
            for i in items:
                d_doc=frappe.get_doc("Design Elements",doc.name)
                dp=frappe.copy_doc(d_doc)
                dp.set("item_code",i['name'])
                dp.set("docstatus",0)
                dp.set("workflow_state","Draft")
                dp.insert()
                dp.submit()
                frappe.db.commit()



@frappe.whitelist()
def create_bulk_elements():
    get_de=frappe.db.sql("""select  name from `tabDesign Elements`   """,as_dict=1)
    for j in get_de:
        print(j)
        doc=frappe.get_doc("Design Elements",j['name'])
        if doc.elements:
            for i in doc.elements:
                d={"doctype":"Elements","project":doc.project}
                if i.pattern_attachment:
                    d['imageb']=i.pattern_attachment
                    
                new=frappe.get_doc(d)
                new.insert()
                frappe.db.commit()

@frappe.whitelist()
def get_urls_sample(docname):
    sites="https://erp.navyacustom.com/"
    doc=frappe.get_doc("Sample",docname)
    img_dup=[]
    images_list=[]
    for i in doc.samples:
        if i.sample_attachment not in img_dup:
            img=sites+i.sample_attachment
            d={"image_url":img}
            images_list.append(d)
            img_dup.append(i.sample_attachment)
            
    return images_list


@frappe.whitelist()
def get_submit(name):
    frappe.enqueue('fashion_navya.utils.doc_event.api_4.submit_bulk',queue='long',name=name,timeout=3000,is_async=True)
    
def submit_bulk(name):
    doc=frappe.get_doc("Bulk Whatsapp",name)
    doc.submit()
    frappe.db.commit()
    frpape.msgprint("Wait a minute")

@frappe.whitelist()
def get_urls_project(docname):
    sites="https://erp.navyacustom.com/"
    get_mood=frappe.db.sql("""select name from `tabMood Board` where project='{}' and docstatus<2  """.format(docname),as_dict=1)
    img_dup=[]
    images_list=[]
    if len(get_mood)!=0:
        for  j in get_mood:
            doc=frappe.get_doc("Mood Board",j['name'])
            images_list.append(doc.drawing_image)
            for i in doc.drawings:
                if i.drawing_attachment not in img_dup:
                    img=sites+i.drawing_attachment
                    d={"image_url":img}
                    images_list.append(d)
                    img_dup.append(i.drawing_attachment)
                    
    return images_list



@frappe.whitelist()
def make_sales_invoice():
    se=frappe.db.sql("""select name  from `tabStock Entry`   where   stock_entry_type='Material Transfer' and  name in (select parent  from `tabStock Entry Detail`  where docstatus=1 and t_warehouse='PStore - NAVYA')   """,as_dict=1)
    d={"doctype":"Sales Invoice","customer":"Navya"}
    d['gst_category']="Registered Regular"
    doc=frappe.get_doc(d)
    items_list=[]
    for i in se:
        print(i['name'])
        sodc=frappe.get_doc("Stock Entry",i['name'])
        for j in sodc.items:
            if j.item_code:
                items_list.append(j.item_code)
            
    items=list(set(items_list))
    if items:
        for k in items:
            if frappe.db.exists("Item",k):
                item=frappe.get_doc("Item",k)
                if item.item_group!="Sample":
                    row = doc.append("items", {})
                    row.item_code=item.name
                    row.item_name=item.item_name
                    row.qty=1
                
    doc.insert()





