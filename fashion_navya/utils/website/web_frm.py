import frappe
import json
from frappe import _
from frappe.model.document import Document, get_controller
from frappe.utils import cint, quoted
from frappe.website.path_resolver import resolve_path

no_cache = 1

from frappe.www.list import (get_list,prepare_filters,get_list_data,get_list_context)

@frappe.whitelist(allow_guest=True)
def get_list_data_custom(
	doctype, txt=None, limit_start=0, fields=None, cmd=None, limit=20, web_form_name=None, **kwargs
):

	limit_start = cint(limit_start)

	if frappe.is_table(doctype):
		frappe.throw(_("Child DocTypes are not allowed"), title=_("Invalid DocType"))



	if not txt and frappe.form_dict.search:
		txt = frappe.form_dict.search
		del frappe.form_dict["search"]


	controller = get_controller(doctype)
	meta = frappe.get_meta(doctype)



	filters = prepare_filters(doctype, controller, kwargs)
	list_context = get_list_context(frappe._dict(), doctype, web_form_name)
	list_context.title_field = getattr(controller, "website", {}).get(
		"page_title_field", meta.title_field or "name"
	)


	if list_context.filters:
		filters.update(list_context.filters)



	_get_list = list_context.get_list or get_list

	#custom code
	filters['docstatus']=1


	kwargs = dict(
		doctype=doctype,
		txt=txt,
		filters=filters,
		limit_start=limit_start,
		limit_page_length=limit,
		order_by=list_context.order_by or "modified desc",
	)

	# allow guest if flag is set
	if not list_context.get_list and (list_context.allow_guest or meta.allow_guest_to_view):
		kwargs["ignore_permissions"] = True


	raw_result = _get_list(**kwargs)


	# list context to be used if called as rendered list
	frappe.flags.list_context = list_context

	return raw_result
