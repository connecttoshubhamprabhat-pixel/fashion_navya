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
                "Pattern":"public/js/custom_script/pattern.js",
                "Payment Entry":"public/js/custom_script/payment_entry.js",
                "Purchase Order":"public/js/custom_script/purchase_order.js",
            }


doctype_list_js ={
        "Work Order":"public/js/list/work_order_list.js",
        "Job Card":"public/js/list/job_card_list.js"

}

# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
doctype_calendar_js ={       
        "Material Request" : "public/js/calendar/material_request_calendar.js",


        }

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
		        "before_save":["fashion_navya.utils.doc_event.sow.set_so__mr","fashion_navya.utils.perm.perm.check_stock_warehouse_source","fashion_navya.utils.doc_event.api_2.fetch_val","fashion_navya.utils.doc_event.stock.fetch_price_sed","fashion_navya.utils.doc_event.st.remove_serial_no","fashion_navya.utils.doc_event.stock.count_qty_noc","fashion_navya.utils.doc_event.stock.check_work_flow"],
               "after_insert":["fashion_navya.utils.perm.perm.check_stock_warehouse_source"],
               "on_cancel":["fashion_navya.utils.doc_event.item.update_item"],
               #"before_insert":["fashion_navya.utils.doc_event.api_1.update_putway_rule"],
               "on_submit":["fashion_navya.utils.doc_event.wo.fetch_status_in_wo","fashion_navya.utils.doc_event.item.update_item","fashion_navya.utils.doc_event.stock.set_val_rate_item","fashion_navya.utils.doc_event.stock.create_tag_m","fashion_navya.utils.doc_event.stock.updte_incharge_wo","fashion_navya.utils.doc_event.stock.throw_error_se","fashion_navya.utils.perm.perm.check_stock_warehouse_target"],
	},
    "POS Invoice":{
            "after_insert":["fashion_navya.utils.doc_event.pos.check_for_sample","fashion_navya.utils.doc_event.pos.check_discount","fashion_navya.utils.doc_event.reserv.reserve_stock_pos","fashion_navya.utils.overides.pos.set_warehouse_split_qty"],
            "before_submit":["fashion_navya.utils.doc_event.item.update_item"],
        },
    "Sales Order":{
        "before_update_after_submit":["fashion_navya.utils.doc_event.so.udpate_val_for_send_notify","fashion_navya.utils.doc_event.api_1.update_del_date_so","fashion_navya.utils.doc_event.so.check_sample_items"],
        "before_submit":["fashion_navya.utils.doc_event.so.check_sample_items"],
        "on_cancel":["fashion_navya.utils.doc_event.so.delete_item_so"],
	"on_trash":["fashion_navya.utils.doc_event.so.delete_item_so"],
    },
    "Stock Ledger Entry":{
        #"validate":["fashion_navya.utils.doc_event.item.custom_title_fields"],
    },
    "Subcontracting Order":{
        "validate":["fashion_navya.utils.doc_event.suborder.only_take_kit_item"],
    },
    "Work Order":{
        "autoname":["fashion_navya.utils.doc_event.wo.autoname_wo_custom"],
        "validate":["fashion_navya.utils.doc_event.wo.replace_items_wo","fashion_navya.utils.doc_event.api_2.set_so_mr","fashion_navya.utils.doc_event.wo.fetch_attributes_so"],
        "before_submit":["fashion_navya.utils.doc_event.api_1.set_warehouse_wo","fashion_navya.utils.doc_event.wo.check_before_submit_disbaled_item"],
        "on_update":["fashion_navya.utils.doc_event.api_2.set_so_mr","fashion_navya.utils.doc_event.wo.fetch_msrement"],
        "before_save":["fashion_navya.utils.doc_event.api_1.set_warehouse_wo","fashion_navya.utils.doc_event.wo.set_parent_item","fashion_navya.utils.doc_event.custom.name_fetch_wo","fashion_navya.utils.doc_event.wo.fetch_msrement"],
        "after_insert":["fashion_navya.utils.doc_event.api_1.set_warehouse_wo","fashion_navya.utils.doc_event.wo.replace_items_wo","fashion_navya.utils.overides.mr.send_nofify_wo","fashion_navya.utils.doc_event.production.wo_stop_pp","fashion_navya.utils.doc_event.api_2.set_so_mr"],
    },
    "Document Record":{
        "after_insert":["fashion_navya.utils.doc_event.docrecord.fetch_po_items_doc"],
    },
    "Payment Order":{
        "validate":["fashion_navya.utils.doc_event.pay_order.calculate_total_amount"],

    },
    "Payment Entry":{
        "on_submit":["fashion_navya.utils.doc_event.api_3.check_amount_so","fashion_navya.utils.doc_event.so.make_mr_so"],
        "on_cancel":["fashion_navya.utils.doc_event.api_3.cancel_mr_unlink"],
        "after_insert":["fashion_navya.utils.doc_event.api_3.check_amount_so","fashion_navya.utils.doc_event.pe.check_duplicate_entry"],
        "before_save":["fashion_navya.utils.doc_event.pe.set_account_by_user"],
    },
    "Bank Deposit Slip":{
    "on_submit":["fashion_navya.utils.doc_event.api_1.submit_all_pe"],
    "validate":["fashion_navya.utils.doc_event.api_1.calculate_total_amount"],
    },
    "Purchase Order":{
        "before_save":["fashion_navya.utils.doc_event.po.check_automated_po","fashion_navya.utils.doc_event.api_2.check_work_order_status","fashion_navya.utils.doc_event.po.set_sell_item_po"],
        "before_submit":["fashion_navya.utils.doc_event.po.get_wo_set_po","fashion_navya.utils.doc_event.sq.fetch_job_card_po"],
        "on_trash":["fashion_navya.utils.doc_event.po.check_delete_draft"],
        "after_insert":["fashion_navya.utils.doc_event.api_3.fetch_items_sq","fashion_navya.utils.doc_event.po.set_sell_item_po"],
        "before_update_after_submit":["fashion_navya.utils.doc_event.sub.update_rate_after_submit"],
    },
    "Item Tag":{
        #"before_save":["fashion_navya.utils.doc_event.stock.check_item_is_ma"],
    },
    "Item":{
           "on_update":["fashion_navya.utils.doc_event.kit.set_project_kit","fashion_navya.utils.doc_event.item.custom_descrip"],
            "after_delete":["fashion_navya.utils.doc_event.item.delete_files"],
            "before_save":["fashion_navya.utils.doc_event.item.check_subconracted","fashion_navya.utils.doc_event.api_1.check_duplciate","fashion_navya.utils.doc_event.kit.make_all_kit_for_item","fashion_navya.utils.doc_event.test.check_subconrcat","fashion_navya.utils.doc_event.item.make_kit_item_parent_save","fashion_navya.utils.doc_event.item.make_add_kt","fashion_navya.utils.doc_event.item.fetched_warehouse_qty_w","fashion_navya.utils.doc_event.item.renamedoc"],
            "after_insert":["fashion_navya.utils.doc_event.kit.set_project_by","fashion_navya.utils.doc_event.item.check_subconracted","fashion_navya.utils.doc_event.api_1.check_duplciate","fashion_navya.utils.doc_event.kit.make_all_kit_for_item","fashion_navya.utils.doc_event.items.make_bom_kit_new","fashion_navya.utils.doc_event.item.make_kit_item_parent","fashion_navya.utils.doc_event.item.set_item_project_reorder"],
            "on_delete":["fashion_navya.utils.doc_event.item.remove_item_rtw"],

        },
	"Timesheet":{
		"after_insert":["fashion_navya.utils.doc_event.jc.se_check_all","fashion_navya.utils.doc_event.timesheet.job_card","fashion_navya.utils.doc_event.timesheet.office_time_start_end"],
                "before_submit":["fashion_navya.utils.doc_event.timesheet.check_hours_diff","fashion_navya.utils.doc_event.timesheet.office_time_start_end"],

},
        "Payment Imprest":{
                "before_save":["fashion_navya.utils.doc_event.api_1.fetch_amount_pim"],

                },
        "Pattern":{
                "after_insert":["fashion_navya.utils.doc_event.pattern.check_sheet_apprved","fashion_navya.utils.doc_event.pattern.fetch_silvit"],
                "on_update":["fashion_navya.utils.doc_event.pattern.pattern_validation"],
                "before_save":["fashion_navya.utils.doc_event.pattern.set_location_pttrn","fashion_navya.utils.doc_event.pattern.check_sheet_apprved","fashion_navya.utils.doc_event.pattern.pattern_not_dup"],

                },
        "File":{
            "after_insert":["fashion_navya.utils.overides.file.check_file_type","fashion_navya.utils.doc_event.file.check_idraw_file"],

                },

        "Purchase Receipt":{
                "before_save":["fashion_navya.utils.doc_event.pr.set_kit_parent_pr"],
                "after_insert":["fashion_navya.utils.doc_event.pr.perm_check_pr"],
                "before_submit":["fashion_navya.utils.doc_event.po.subcontacted_check","fashion_navya.utils.doc_event.pr.perm_check_pr"],

                },
        "Sales Invoice":{
              "before_submit":["fashion_navya.utils.doc_event.pe.create_pe_for_internal_si"],
              "on_cancel":["fashion_navya.utils.doc_event.si.cancel_doc_si_series","fashion_navya.utils.doc_event.pe.cancel_pe_si"],
              "on_submit":["fashion_navya.utils.doc_event.item.update_item_si"],
                #"before_submit":["fashion_navya.utils.doc_event.si.make_new_si_id"],

                },
        "Project":{
                "after_insert":["fashion_navya.utils.doc_event.todo.create_todo"],
                "before_save":["fashion_navya.utils.doc_event.project.pending_qty_kit","fashion_navya.utils.doc_event.project.calculated_qty_project","fashion_navya.utils.doc_event.task.set_is_urgent_task"],

                },

            "Physical Stock Count":{
                        "before_submit":["fashion_navya.utils.doc_event.phy.remove_other_wstock","fashion_navya.utils.doc_event.phy.calculate_stock_phy"],
                        "after_insert":["fashion_navya.utils.doc_event.phy.collab_items"],
                        #"before_save":["fashion_navya.utils.doc_event.phy.remove_other_wstock"],

            },
            "BOM":{
               # "before_save":["fashion_navya.utils.doc_event.custom.make_rtw_item"],
               "before_save":["fashion_navya.utils.doc_event.pattern.set_type_bom","fashion_navya.utils.doc_event.bom.fetch_fabrice_ptt"],
               "before_submit":["fashion_navya.utils.doc_event.api_3.set_conver_item","fashion_navya.utils.doc_event.api_1.make_default_bom","fashion_navya.utils.doc_event.api_1.make_mr_first_bom","fashion_navya.utils.doc_event.bom.before_submit_check_kit","fashion_navya.utils.doc_event.mr.check_is_bom_mr","fashion_navya.utils.doc_event.api_2.template_bom"],
               "after_insert":["fashion_navya.utils.doc_event.item.submit_bom_project","fashion_navya.utils.doc_event.wo.replace_items_bom","fashion_navya.utils.doc_event.bom.remove_disabled_items"],
               "on_cancel":["fashion_navya.utils.doc_event.pattern.check_cancel_bom","fashion_navya.utils.doc_event.mr.uncheck_is_bom_mr"],

                },
            "Delivery Note":{

                "on_submit":["fashion_navya.utils.doc_event.item.update_item"],
                #"after_insert":["fashion_navya.utils.doc_event.reserv.reserve_stock_pos"],
                    },
            "Subcontracting Order":{
                #"before_submit":["fashion_navya.utils.doc_event.sub.fetch_work_order"],
                "before_save":["fashion_navya.utils.doc_event.api_2.get_wo_sub"],

            },
		"Journal Entry":{
			"before_save":["fashion_navya.utils.doc_event.jv.jv_refund_check"],

	},
                "Customer":{
                            "before_insert":["fashion_navya.utils.doc_event.customer.customer_no_check_exists"],
			    "before_save":["fashion_navya.utils.doc_event.api_2.set_silvit_cus","fashion_navya.utils.doc_event.customer.customer_no_check_exists"],
                "after_insert":["fashion_navya.utils.doc_event.customer.create_contact"],
                "on_update":["fashion_navya.utils.doc_event.customer.contact_update"],

                        },
                "Estimate Sheet":{
                       # "after_insert":["fashion_navya.utils.doc_event.estimate.check_estimate_paid"],

                        },
                "Timesheet Missing":{
                            "after_insert":["fashion_navya.utils.doc_event.miss.add_total_hours","fashion_navya.utils.doc_event.ts.check_date_hr_diff","fashion_navya.utils.doc_event.timesheet.add_diff_miss"],
                            "before_save":["fashion_navya.utils.doc_event.ts.check_date_hr_diff","fashion_navya.utils.doc_event.timesheet.nine_hours_validations"],
                        },
                "Supplier Quotation":{
                            "before_submit":["fashion_navya.utils.doc_event.sq.fetch_job_card"],

                        },
                "Production Plan":{
                        "before_save":["fashion_navya.utils.doc_event.production.remove_disabled"],
                        #"after_insert":["fashion_navya.utils.doc_event.production.production_plan_set_fg_warehouse"],
                        #"before_submit":["fashion_navya.utils.doc_event.production.production_plan_set_fg_warehouse"],
                        #"before_insert":["fashion_navya.utils.doc_event.production.remove_without_bom"],

                        },
                        "Maintenance Visit":{
                                "after_insert":["fashion_navya.utils.doc_event.mv.fetch_attribues"],
                                "before_submit":["fashion_navya.utils.doc_event.mv.make_mr_from_mv","fashion_navya.utils.doc_event.mv.fetch_attribues","fashion_navya.utils.doc_event.mv.custom_maintence_visit"],


                                },
                            "Material Request":{
                                    "before_submit":["fashion_navya.utils.doc_event.mr.check_bom_project","fashion_navya.utils.doc_event.sow.set_warehouse_target_mr","fashion_navya.utils.doc_event.mr.mr_links_transfer","fashion_navya.utils.doc_event.todo.create_todo_mr_bom","fashion_navya.utils.doc_event.mr.check_bom_mr","fashion_navya.utils.doc_event.api_2.customer_added_mr"],
                                    "before_save":["fashion_navya.utils.doc_event.wo.fetch_msrement_mr","fashion_navya.utils.doc_event.api_2.status_updated"],
                                    "after_insert":["fashion_navya.utils.doc_event.so.make_mr_manual_so"],
                                    #"before_update_after_submit":["fashion_navya.utils.doc_event.wo.fetch_msrement_mr"],

                                    },

                            "ToDo":{
                                    "before_insert":["fashion_navya.utils.doc_event.api_3.todo_link_withproject"],


                                },
                            "Purchase Invoice":{
                                    #"before_submit":["fashion_navya.utils.doc_event.pi.link_setup_subcontrcat"],


                                    },
                            "Item Price":{
                                        "on_update":["fashion_navya.utils.doc_event.item.make_price_from_template","fashion_navya.utils.doc_event.api_1.update_price_item"],

                                    },
                            "Address":{
                                    "on_update":["fashion_navya.utils.doc_event.address.check_is_shipping"],

                                    },
                            "Job Card":{
                                    "before_submit":["fashion_navya.utils.doc_event.job_card.qty_check_jc"],
                                    "validate":["fashion_navya.utils.doc_event.jc.se_check_all_jc"],
                                    "on_submit":["fashion_navya.utils.doc_event.job_card.make_timesheet_all"],

                                    },
                            "Consolidated physical Stock Count":{
                                    "on_update_after_submit":["fashion_navya.utils.doc_event.phy.update_after_submits_all"],

                                    },
                            "Catalogue":{
                                        "before_save":["fashion_navya.utils.doc_event.api_1.fetch_net_stock"],
                                },
                            "Notification Log":{
                                    "before_save":["fashion_navya.utils.doc_event.api_1.set_read_flilter_logs"],

                                    },
                            "BOM Creator":{
                                    "before_save":["fashion_navya.utils.doc_event.item.set_validation_bomc","fashion_navya.utils.doc_event.item.fabric_fetch_pattt"],

                                    },

}

# Scheduled Tasks
# ---------------

scheduler_events = {
#	"all": [
#		"fashion_navya.tasks.all"
#	],
	"daily": [
	    "fashion_navya.utils.overides.mr.send_nofify_mr_custom","fashion_navya.utils.doc_event.item.delete_item_customise","fashion_navya.utils.doc_event.delivery.set_notify_todo"
	],
#	"hourly": [
#		"fashion_navya.tasks.hourly"
#	],
#	"weekly": [
#		"fashion_navya.tasks.weekly"
#	],
#	"monthly": [
#		"fashion_navya.tasks.monthly"
#	],

    "cron":{
            "12 22 * * *": [
                "fashion_navya.utils.doc_event.cron.today_cash_amount",
        ],
            "30 23 * * *":[
                    "fashion_navya.utils.doc_event.item.fetched_warehouse_sch",

                ],

            "40 23 * * *":[

                    "fashion_navya.utils.overides.mr.automated_plan",

                ],
            "50 23 * * *":[

                    "fashion_navya.utils.overides.mr.automated_plan_without_so",

                ],
            "40 22 * * *":[
                    "fashion_navya.utils.doc_event.project.get_not_started_pro_bulk_auto",
                ],
            "30 04 * * *":[
                    "fashion_navya.utils.doc_event.mr.project_wise_divide_auto",
                ],
            "20 21 * * *":[
                    "fashion_navya.utils.doc_event.mr.project_wise_divide_auto",

                ],

            "20 04 * * *":[

                    "fashion_navya.utils.doc_event.api_1.update_stock_cron",

                ],

            "38 20 * * *":[
                        "fashion_navya.utils.doc_event.cron.update_project_cron",

                ],


        }


 }

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



override_doctype_class = {
    "POS Invoice":"fashion_navya.utils.overides.posi.CustomPOSInvoice",
    "File":"fashion_navya.utils.overides.file.CustomFile",
    "BOM Creator":"fashion_navya.utils.overides.bomc.CustomBOMCreator",
    "Production Plan":["fashion_navya.utils.overides.mr.CustomProductionPlan"],

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
