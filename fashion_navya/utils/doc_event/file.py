import  frappe


@frappe.whitelist()
def check_file_type(doc,method):
	if doc.file_name:
                namesplit=doc.file_name.split(".")
                type_list=['psd','idraw']
                if namesplit[-1] in type_list:
                        if doc._is_private==0:
                                frappe.throw("Sorry ,The file should be uploaded as private")


@frappe.whitelist()
def check_idraw_file(doc,method):
	if doc.file_name:
		namesplit=doc.file_name.split(".")
		type_list=['idraw']
		if namesplit[-1] in type_list:
			frappe.throw("Sorry ,Idraw File is not uploding yet")

