from . import __version__ as app_version

app_name = "fashion_navya"
app_title = "Fashion Navya"
app_publisher = "pawasthy11@gmail.com"
app_description = "navya fashion"
app_email = "pawasthy11@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------


app_include_js = [
        "fashion_navya.bundle.js",
]

# include js, css files in header of desk.html
# app_include_css = "/assets/fashion_navya/css/fashion_navya.css"
# app_include_js = "/assets/fashion_navya/js/fashion_navya.js"

# include js, css files in header of web template
# web_include_css = "/assets/fashion_navya/css/fashion_navya.css"
# web_include_js = "/assets/fashion_navya/js/fashion_navya.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "fashion_navya/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views


doctype_js = {
                "BOM":"public/js/custom_script/bom.js",
                "Work Order":"public/js/custom_script/work_order.js",
                "Stock Entry":"public/js/custom_script/stock_entry.js",
                "Item":"public/js/custom_script/item.js",
                "Sales Order":"public/js/custom_script/sales_order.js",
            }


doctype_list_js ={
        "Work Order":"public/js/list/work_order_list.js",
        "Job Card":"public/js/list/job_card_list.js"

}

# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "fashion_navya.utils.jinja_methods",
#	"filters": "fashion_navya.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "fashion_navya.install.before_install"
# after_install = "fashion_navya.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "fashion_navya.uninstall.before_uninstall"
# after_uninstall = "fashion_navya.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "fashion_navya.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Stock Entry": {
		        "before_save":["fashion_navya.utils.doc_event.stock.check_work_flow","fashion_navya.utils.doc_event.stock.warehouse_check_se"],
               "after_insert":["fashion_navya.utils.perm.perm.check_stock_warehouse_source"],
               "on_submit":["fashion_navya.utils.doc_event.stock.throw_error_se","fashion_navya.utils.perm.perm.check_stock_warehouse_target"],
	},
    "POS Invoice":{
            "after_insert":["fashion_navya.utils.overides.pos.set_warehouse_split_qty"],
        },
    "Sales Order":{
        #"after_insert":["fashion_navya.utils.doc_event.sales_order.show_live_update"],
        "on_submit":["fashion_navya.utils.doc_event.sales_order.make_workorder_pre","fashion_navya.utils.doc_event.sales_order.make_se_transfer"]
    },
    "Stock Ledger Entry":{
        #"validate":["fashion_navya.utils.doc_event.item.custom_title_fields"],
    },
    "Subcontracting Order":{
        "validate":["fashion_navya.utils.doc_event.suborder.only_take_kit_item"],
    },
    "Work Order":{
        "validate":["fashion_navya.utils.doc_event.work.check_item_no_subo"],
    },
    "Document Record":{
        "after_insert":["fashion_navya.utils.doc_event.docrecord.fetch_po_items_doc"],
    },
    "Payment Order":{
        "validate":["fashion_navya.utils.doc_event.pay_order.calculate_total_amount"],

    },
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"fashion_navya.tasks.all"
#	],
#	"daily": [
#		"fashion_navya.tasks.daily"
#	],
#	"hourly": [
#		"fashion_navya.tasks.hourly"
#	],
#	"weekly": [
#		"fashion_navya.tasks.weekly"
#	],
#	"monthly": [
#		"fashion_navya.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "fashion_navya.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	#"frappe.desk.doctype.event.event.get_events": "fashion_navya.event.get_events"
       #"frappe.desk.form.load.getdoc":"fashion_navya.utils.overides.load.getdoc",
       "frappe.www.list.get_list_data":"fashion_navya.utils.website.web_frm.get_list_data_custom",
       "erpnext.selling.page.point_of_sale.point_of_sale.get_items":"fashion_navya.utils.overides.pos.get_items_custom",
       "erpnext.accounts.doctype.pos_invoice.pos_invoice.get_stock_availability":"fashion_navya.utils.overides.pos.get_stock_availability_custom",
}

# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "fashion_navya.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["fashion_navya.utils.before_request"]
# after_request = ["fashion_navya.utils.after_request"]

# Job Events
# ----------
# before_job = ["fashion_navya.utils.before_job"]
# after_job = ["fashion_navya.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"fashion_navya.auth.validate"
# ]
