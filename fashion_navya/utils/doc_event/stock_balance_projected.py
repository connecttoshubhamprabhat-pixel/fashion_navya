import frappe
from frappe import _
from frappe.utils import flt, today
from pypika.terms import ExistsCriterion
from erpnext.accounts.doctype.pos_invoice.pos_invoice import get_pos_reserved_qty
from erpnext.stock.utils import (
	is_reposting_item_valuation_in_progress,
	update_included_uom_in_report,
)






@frappe.whitelist()
def get_bin_list(filters=None):
    if not filters:
        return

    bin = frappe.qb.DocType("Bin")
    query = (
        frappe.qb.from_(bin)
		.select(
			bin.item_code,
			bin.warehouse,
			bin.actual_qty,
			bin.planned_qty,
			bin.indented_qty,
			bin.ordered_qty,
			bin.reserved_qty,
			bin.reserved_qty_for_production,
			bin.reserved_qty_for_sub_contract,
			bin.reserved_qty_for_production_plan,
			bin.projected_qty,
		)
		.orderby(bin.item_code, bin.warehouse)
	)

    if filters.item_code:
        query = query.where(bin.item_code == filters.item_code and not (actual_qty=0 and reserved_qty=0))


    if filters.warehouse:
        warehouse_details = frappe.db.get_value(
			"Warehouse", filters.warehouse, ["lft", "rgt"], as_dict=1
		)

        if warehouse_details:
			wh = frappe.qb.DocType("Warehouse")
			query = query.where(
				ExistsCriterion(
					frappe.qb.from_(wh)
					.select(wh.name)
					.where(
						(wh.lft >= warehouse_details.lft)
						& (wh.rgt <= warehouse_details.rgt)
						& (bin.warehouse == wh.name)
					)
				)
			)


    bin_list = query.run(as_dict=True)
    print(bin_list,"bin_list")
    return bin_list
