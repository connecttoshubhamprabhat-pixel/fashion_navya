import frappe
from frappe.desk.form.load import getdoc,set_link_titles,run_onload,get_docinfo
import json
from urllib.parse import quote
import frappe.defaults
import frappe.desk.form.meta
import frappe.share
import frappe.utils
from frappe import _, _dict
from frappe.desk.form.document_follow import is_document_followed
from frappe.model.utils import is_virtual_doctype
from frappe.model.utils.user_settings import get_user_settings
from frappe.permissions import get_doc_permissions
from frappe.utils.data import cstr



@frappe.whitelist()
def getdoc(doctype, name, user=None):
    user=frappe.session.user
    if doctype=="Item" and user in ['neha@navyacustom.com']:
        frappe.throw("Not Allowed")

    if not (doctype and name):
        raise Exception("doctype and name required!")


    if not name:
        name = doctype

    if not is_virtual_doctype(doctype) and not frappe.db.exists(doctype, name):
        return []


    doc = frappe.get_doc(doctype, name)
    run_onload(doc)


    if not doc.has_permission("read"):
        frappe.flags.error_message = _("Insufficient Permission for {0}").format(
			frappe.bold(doctype + " " + name)
		)
        raise frappe.PermissionError(("read", doctype, name))

	# ignores system setting (apply_perm_level_on_api_calls) unconditionally to maintain backward compatibility
    doc.apply_fieldlevel_read_permissions()

	# add file list
    doc.add_viewed()
    get_docinfo(doc)


    doc.add_seen()
    set_link_titles(doc)
    if frappe.response.docs is None:
        frappe.local.response = _dict({"docs": []})

    frappe.response.docs.append(doc)
