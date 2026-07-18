// // // Copyright (c) 2026, pawasthy11@gmail.com and contributors
// // // For license information, please see license.txt

// // frappe.query_reports["User Warehouse Stock Balance"] = {
// // 	"filters": [

// // 	]
// // };














// frappe.query_reports["User Warehouse Stock Balance"] = {

//     filters: [

//         {
//             fieldname: "user",
//             label: __("User"),
//             fieldtype: "Link",
//             options: "User",
//             reqd: 1
//         },

//         {
//             fieldname: "company",
//             label: __("Company"),
//             fieldtype: "Link",
//             options: "Company",
//             default: frappe.defaults.get_default("company")
//         },

//         {
//             fieldname: "from_date",
//             label: __("From Date"),
//             fieldtype: "Date",
//             reqd: 1,
//             default: frappe.datetime.add_months(frappe.datetime.get_today(), -1)
//         },

//         {
//             fieldname: "to_date",
//             label: __("To Date"),
//             fieldtype: "Date",
//             reqd: 1,
//             default: frappe.datetime.get_today()
//         },

//         {
//             fieldname: "item_group",
//             label: __("Item Group"),
//             fieldtype: "Link",
//             options: "Item Group"
//         },

//         {
//             fieldname: "item_code",
//             label: __("Item"),
//             fieldtype: "Link",
//             options: "Item"
//         }
//     ],

//     formatter: function(value, row, column, data, default_formatter) {

//         value = default_formatter(value, row, column, data);

//         // Skip fixed columns
//         let fixed_columns = [
//             "user",
//             "item_code",
//             "item_name"
//         ];

//         if (!fixed_columns.includes(column.fieldname) && data) {

//             let qty = data[column.fieldname];

//             if (qty > 0) {

//                 value = `<span style="
//                     color: #058203;
//                     // font-weight: bold;
//                 ">${value}</span>`;

//             } else if (qty < 0) {

//                 value = `<span style="
//                     color: #ff0000;
//                     // font-weight: bold;
//                 ">${value}</span>`;

//             } else if (qty == 0) {

//                 value = `<span style="
//                     color: #ffda1f;
//                     // font-weight: bold;
//                 ">${value}</span>`;
//             }
//         }

//         return value;
//     }
// };






































// frappe.query_reports["User Warehouse Stock Balance"] = {

//     onload: function(report) {

//         report.set_filter_value("warehouse", [

//             "New store - NAVYA",
//             "Default Transit - NAVYA",
//             "Kit Store - NAVYA",
//             "Navya Store Office - NAVYA",
//             "Purchase Station - NAVYA"

//         ]);

//     },

//     filters: [

//         {
//             fieldname: "user",
//             label: __("User"),
//             fieldtype: "Link",
//             options: "User",
//             reqd: 1
//         },

//         {
//             fieldname: "warehouse",
//             label: __("Warehouses"),
//             fieldtype: "MultiSelectList",
//             width: "300",

//             get_data: function(txt) {

//                 return frappe.db.get_link_options(
//                     "Warehouse",
//                     txt,
//                     {}
//                 );

//             }
//         },

//         {
//             fieldname: "company",
//             label: __("Company"),
//             fieldtype: "Link",
//             options: "Company",
//             default: frappe.defaults.get_default("company")
//         },

//         {
//             fieldname: "from_date",
//             label: __("From Date"),
//             fieldtype: "Date",
//             reqd: 1,
//             default: frappe.datetime.add_months(
//                 frappe.datetime.get_today(),
//                 -1
//             )
//         },

//         {
//             fieldname: "to_date",
//             label: __("To Date"),
//             fieldtype: "Date",
//             reqd: 1,
//             default: frappe.datetime.get_today()
//         },

//         {
//             fieldname: "item_group",
//             label: __("Item Group"),
//             fieldtype: "Link",
//             options: "Item Group"
//         },

//         {
//             fieldname: "item_code",
//             label: __("Item"),
//             fieldtype: "Link",
//             options: "Item"
//         }
//     ],

//     formatter: function(
//         value,
//         row,
//         column,
//         data,
//         default_formatter
//     ) {

//         value = default_formatter(
//             value,
//             row,
//             column,
//             data
//         );

//         // Fixed columns
//         let fixed_columns = [

//             "user",
//             "item_code",
//             "item_name"

//         ];

//         if (
//             !fixed_columns.includes(column.fieldname)
//             && data
//         ) {

//             let qty = data[column.fieldname];

//             if (qty > 0) {

//                 value = `
//                     <span style="color:#058203;">
//                         ${value}
//                     </span>
//                 `;

//             } else if (qty < 0) {

//                 value = `
//                     <span style="color:#ff0000;">
//                         ${value}
//                     </span>
//                 `;

//             } else if (qty == 0) {

//                 value = `
//                     <span style="color:#ffda1f;">
//                         ${value}
//                     </span>
//                 `;
//             }
//         }

//         return value;
//     }
// };








































frappe.query_reports["User Warehouse Stock Balance"] = {

    onload: function(report) {

        let user_filter = report.get_filter("user");

        user_filter.$input.on("change", function() {

            let user = report.get_filter_value("user");

            if (!user) {
                report.set_filter_value("warehouse", []);
                return;
            }

            frappe.call({
                method: "fashion_navya.fashion_navya.report.user_warehouse_stock_balance.user_warehouse_stock_balance.get_user_warehouses",
                args: {
                    user: user
                },
                callback: function(r) {

                    if (r.message) {

                        report.set_filter_value(
                            "warehouse",
                            r.message
                        );

                    }
                }
            });

        });

    },

    filters: [

        {
            fieldname: "user",
            label: __("User"),
            fieldtype: "Link",
            options: "User",
            reqd: 1
        },

        {
            fieldname: "warehouse",
            label: __("Warehouses"),
            fieldtype: "MultiSelectList",
            width: 300,

            get_data: function(txt) {

                return frappe.db.get_link_options(
                    "Warehouse",
                    txt
                );

            }
        },

        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_default("company")
        },

        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.add_months(
                frappe.datetime.get_today(),
                -1
            )
        },

        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.get_today()
        },

        {
            fieldname: "item_group",
            label: __("Item Group"),
            fieldtype: "Link",
            options: "Item Group"
        },

        {
            fieldname: "item_code",
            label: __("Item"),
            fieldtype: "Link",
            options: "Item"
        }

    ],

    formatter: function(
        value,
        row,
        column,
        data,
        default_formatter
    ) {

        value = default_formatter(
            value,
            row,
            column,
            data
        );

        let fixed_columns = [
            "user",
            "item_code",
            "item_name"
        ];

        if (
            !fixed_columns.includes(column.fieldname)
            && data
        ) {

            let qty = data[column.fieldname];

            if (qty > 0) {

                value = `
                    <span style="color:#058203;">
                        ${value}
                    </span>
                `;

            } else if (qty < 0) {

                value = `
                    <span style="color:#ff0000;">
                        ${value}
                    </span>
                `;

            } else if (qty == 0) {

                value = `
                    <span style="color:#ffda1f;">
                        ${value}
                    </span>
                `;

            }
        }

        return value;
    }
};




















