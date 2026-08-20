frappe.ui.form.on("Item Price", {
	setup(frm) {
		// ERPNext v16 filters out template items. Navya prices templates and
		// propagates their rates to variants through the existing on_update hooks.
		frm.set_query("item_code", () => ({
			filters: {
				disabled: 0,
			},
		}));
	},
});
