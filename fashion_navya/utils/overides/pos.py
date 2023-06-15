import frappe
from frappe.utils import cint
from frappe.utils.nestedset import get_root_of
from erpnext.selling.page.point_of_sale.point_of_sale import (search_by_term,get_conditions,get_item_group_condition)
from erpnext.accounts.doctype.pos_invoice.pos_invoice import (get_bin_qty,get_pos_reserved_qty,get_bundle_availability)


@frappe.whitelist()
def get_stock_availability_custom(item_code, warehouse):
    #frappe.throw("helo ps 12")
    group_warehouses = frappe.get_doc('Warehouse',warehouse)
    if group_warehouses.is_group==1:
        child_warehouses = frappe.get_all('Warehouse', filters={'parent_warehouse':warehouse},fields=['name'])
        bin_qty_total=0
        pos_qtyr=0
        for c in child_warehouses:
             warehouse=c['name']
             if frappe.db.get_value("Item", item_code, "is_stock_item"):
                 is_stock_item = True
                 bin_qty = get_bin_qty(item_code, warehouse)
                 bin_qty_total+=bin_qty
                 pos_sales_qty = get_pos_reserved_qty(item_code, warehouse)
                 pos_qtyr+=pos_sales_qty

        remain_qty=bin_qty_total-pos_qtyr
        if frappe.db.get_value("Item", item_code, "is_stock_item"):
            if remain_qty>0:
                return remain_qty, is_stock_item
            else:
                return 0, is_stock_item

        else:
            return 0

    if group_warehouses.is_group==0:
        group_zero = frappe.get_doc('Warehouse',warehouse)
        child_warehouses =frappe.get_all('Warehouse', filters={'parent_warehouse':group_zero.parent_warehouse},fields=['name'])
        bin_qty_total=0
        pos_qtyr=0
        if len(child_warehouses)!=0:
            for c in child_warehouses:
                 warehouse=c['name']
                 if frappe.db.get_value("Item", item_code, "is_stock_item"):
                     is_stock_item = True
                     bin_qty = get_bin_qty(item_code, warehouse)
                     bin_qty_total+=bin_qty
                     pos_sales_qty = get_pos_reserved_qty(item_code, warehouse)
                     pos_qtyr+=pos_sales_qty

        remain_qty=bin_qty_total-pos_qtyr
        if frappe.db.get_value("Item", item_code, "is_stock_item"):
            if remain_qty>0:
                return remain_qty, is_stock_item
            else:
                return 0, is_stock_item

        else:
            return 0





@frappe.whitelist()
def get_items_custom(start, page_length, price_list, item_group, pos_profile, search_term=""):
    warehouse, hide_unavailable_items = frappe.db.get_value(
		"POS Profile", pos_profile, ["warehouse", "hide_unavailable_items"]
	)

    ##frappe.throw("helo ps 71")
    result = []
    group_warehouses = frappe.get_doc('Warehouse',warehouse)
    total_warehouse=[]
    if group_warehouses.is_group==1:
        child_warehouses =frappe.get_all('Warehouse', filters={'parent_warehouse':warehouse},fields=['name'])
        for ws in child_warehouses:
            total_warehouse.append(ws['name'])
    else:
        group_whse = frappe.get_doc('Warehouse',warehouse)
        child_warehouses =frappe.get_all('Warehouse', filters={'parent_warehouse':group_whse.parent_warehouse},fields=['name'])
        for ws in child_warehouses:
            total_warehouse.append(ws['name'])


    if search_term:
        result = search_by_term(search_term, warehouse, price_list) or []
        if result:
            return result


    if not frappe.db.exists("Item Group", item_group):
        item_group = get_root_of("Item Group")


    condition = get_conditions(search_term)
    condition += get_item_group_condition(pos_profile)

    lft, rgt = frappe.db.get_value("Item Group", item_group, ["lft", "rgt"])
    bin_join_selection, bin_join_condition = "", ""


    if hide_unavailable_items:
        bin_join_selection = ", `tabBin` bin"
        bin_join_condition = (
			"AND bin.warehouse = %(warehouse)s AND bin.item_code = item.name AND bin.actual_qty > 0"
		)


    collect_data=[]
    for wt in total_warehouse:
        warehouse=wt
        items_data = frappe.db.sql(
    		"""
    		SELECT
    			item.name AS item_code,
    			item.item_name,
    			item.description,
    			item.stock_uom,
    			item.image AS item_image,
    			item.is_stock_item
    		FROM
    			`tabItem` item {bin_join_selection}
    		WHERE
    			item.disabled = 0
    			AND item.has_variants = 0
    			AND item.is_sales_item = 1
    			AND item.is_fixed_asset = 0
    			AND item.item_group in (SELECT name FROM `tabItem Group` WHERE lft >= {lft} AND rgt <= {rgt})
    			AND {condition}
    			{bin_join_condition}
    		ORDER BY
    			item.name asc
    		LIMIT
    			{page_length} offset {start}""".format(
    			start=cint(start),
    			page_length=cint(page_length),
    			lft=cint(lft),
    			rgt=cint(rgt),
    			condition=condition,
    			bin_join_selection=bin_join_selection,
    			bin_join_condition=bin_join_condition,
    		),
    		{"warehouse": warehouse},
    		as_dict=1,
    	)
        for wtdata in items_data:
            #print(wtdata)
            collect_data.append(wtdata)




    items_data=collect_data
    #print(collect_data,'collect_data')
    #frappe.throw('aaa')
    if items_data:
        items = [d.item_code for d in items_data]
        item_prices_data = frappe.get_all(
        "Item Price",
			fields=["item_code", "price_list_rate", "currency"],
			filters={"price_list": price_list, "item_code": ["in", items]},
		)


        item_prices = {}
        for d in item_prices_data:
            item_prices[d.item_code] = d


        for item in items_data:
            item_code = item.item_code
            item_price = item_prices.get(item_code) or {}
            item_stock_qty, is_stock_item = get_stock_availability_custom(item_code, warehouse)


            row = {}
            row.update(item)
            row.update(
				{
					"price_list_rate": item_price.get("price_list_rate"),
					"currency": item_price.get("currency"),
					"actual_qty": item_stock_qty,
				}
			)
            result.append(row)

    return {"items": result}




@frappe.whitelist()
def set_warehouse_split_qty(doc,method):
    #frappe.throw('aa')
    from erpnext.stock.dashboard.item_dashboard import get_data
    qty_out=[]
    if doc.pos_profile:
        print(18555555555555)
        all_wareh=[]
        posdoc=frappe.get_doc("POS Profile",doc.pos_profile)
        group_warehouse = frappe.get_doc('Warehouse', posdoc.warehouse)
        if group_warehouse.is_group==1:
            child_warehouses =frappe.get_all('Warehouse', filters={'parent_warehouse':group_warehouse.name},fields=['name'])
            if len(child_warehouses)!=0:
                for m in child_warehouses:
                    all_wareh.append(m)
        if group_warehouse.is_group==0:
            child_warehouses =frappe.get_all('Warehouse', filters={'parent_warehouse':group_warehouse.parent_warehouse},fields=['name'])
            if len(child_warehouses)!=0:
                for m in child_warehouses:
                    all_wareh.append(m)




        print(all_wareh,'child_warehouses')
        for i in doc.items:
            itemcode=i.item_code
            qty_to_release=i.qty
            for w in all_wareh:
                if qty_to_release:
                    print(193333333)
                    whouse=w['name']
                    data_items=get_data(item_code=itemcode,warehouse=whouse)
                    print(data_items,'data_items')
                    if len(data_items)!=0:
                        #print(data_items,'data_items')
                        if data_items[0]['actual_qty']!=0:
                            sub_qty=qty_to_release-data_items[0]['actual_qty']
                            if sub_qty==0:
                                print(1977777777777)
                                qty_to_release=0
                                #frappe.throw("aab")
                                i.db_set("warehouse",data_items[0]['warehouse'], update_modified=False)
                                doc.db_set("set_warehouse",None, update_modified=False)



                            if sub_qty<0:
                                qty_to_release=0
                                print(20222222222)
                                #frappe.throw("aac")
                                i.db_set("warehouse",data_items[0]['warehouse'], update_modified=False)
                                doc.db_set("set_warehouse",None, update_modified=False)
                            if sub_qty>0:
                                #frappe.throw("aad")
                                qty_to_release -=data_items[0]['actual_qty']
                                d={}
                                d['item_code']=itemcode
                                d['qty']=data_items[0]['actual_qty']
                                d['warehouse']=data_items[0]['warehouse']
                                qty_out.append(d)

    if qty_out:
        pass
