frappe.ui.form.on("BOM", "refresh", function(frm) {

	if (cur_frm.doc.scrap__material.length>0){

		console.log('aaaascrap')
    frm.fields_dict['scrap_items'].grid.get_field('item_code').get_query = function(doc, cdt, cdn) {
        var child = locals[cdt][cdn];

        return {
            filters: [
                ['bom', '=', cur_frm.doc.name]]
        }
    }

}
});
