##############################################################################
# Copyright (c) 2025 braintec AG (https://braintec.com)
# All Rights Reserved
#
# Licensed under the AGPL-3.0 (http://www.gnu.org/licenses/agpl.html)
# See LICENSE file for full licensing details.
##############################################################################

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleOnchanges(TransactionCase):
    def test_variant_sale_warnings(self):
        """Warnings & SO/SOL updates products with variant sale warnings are used."""
        partner = self.env["res.partner"].create({"name": "Test"})
        sale_order = self.env["sale.order"].create({"partner_id": partner.id})
        product_with_warning = self.env["product.product"].create(
            {
                "name": "Test Product",
                "variant_sale_line_warn": "warning",
                "variant_sale_line_warn_msg": "Highly corrosive",
            }
        )
        product_with_block_warning = self.env["product.product"].create(
            {
                "name": "Test Product (2)",
                "variant_sale_line_warn": "block",
                "variant_sale_line_warn_msg": "Not produced anymore",
            }
        )

        sale_order_line = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": product_with_warning.id,
            }
        )
        warning = sale_order_line._onchange_product_id_warning()
        self.assertDictEqual(
            warning,
            {
                "warning": {
                    "title": "Warning for Test Product",
                    "message": product_with_warning.variant_sale_line_warn_msg,
                },
            },
        )

        sale_order_line.product_id = product_with_block_warning
        warning = sale_order_line._onchange_product_id_warning()

        self.assertDictEqual(
            warning,
            {
                "warning": {
                    "title": "Warning for Test Product (2)",
                    "message": product_with_block_warning.variant_sale_line_warn_msg,
                },
            },
        )

        self.assertFalse(sale_order_line.product_id.id)
