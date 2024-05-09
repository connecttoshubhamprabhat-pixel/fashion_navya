import frappe

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
    if doc.sheet_no==4:
        get_pattern_img=frappe.db.sql(""" select file_url  from   `tabFile`  where attached_to_doctype='Pattern' and attached_to_name='{}' and attached_to_field='file'  """.format(doc.name),as_dict=1)
        if len(get_pattern_img)!=0:
            d={}
            d['image_url']=sites+get_pattern_img[0]['file_url']
            images_list.append(d)
            
            
            
            
        get_drw_img=frappe.db.sql(""" select file_url  from   `tabFile`  where attached_to_doctype='Drawing' and attached_to_name='{}' and attached_to_field='file'  """.format(doc.drawing),as_dict=1)
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





