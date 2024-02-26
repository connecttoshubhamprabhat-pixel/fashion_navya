import frappe
import os
from pathlib import Path

#delet file from backend folder
@frappe.whitelist()
def delete_files():
    public_folder='/home/frappe/frappe-live/sites/erp.navyacustom.com/public/files'
    private_folder='/home/frappe/frappe-live/sites/erp.navyacustom.com/private/files'
    #files=frappe.db.sql("""select file_name from `tabFile`  where file_url in (select image from `tabStock Entry` where stock_entry_type='Manufacture'  and posting_date between '2021-01-01' and '2023-12-30') """,as_dict=1)
    files=frappe.db.sql("""select file_name from `tabFile`  where file_url in (select image from `tabImage View` where event is not null  ) """,as_dict=1)
    files=frappe.db.sql("""select file_name from `tabFile`  where attached_to_doctype='Document Record'  """,as_dict=1)
    if files:
        for i in files:
            myfile=public_folder+"/"+i['file_name']
            if os.path.isfile(myfile):
                print(myfile,"feb19")
                os.remove(myfile)
