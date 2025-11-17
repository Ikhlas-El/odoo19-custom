# -*- coding: utf-8 -*-
from odoo import models, api


class StockLot(models.Model):
    _inherit = 'stock.lot'

    @api.model_create_multi
    def create(self, vals_list):
        """Override to use product sequence when creating lots"""
        for vals in vals_list:
            # Only override if no name is provided or if it looks like default sequence
            if vals.get('product_id'):
                product = self.env['product.product'].browse(vals['product_id'])

                # Check if product has OCA lot_sequence_id
                if hasattr(product, 'lot_sequence_id') and product.lot_sequence_id:
                    # If no name provided, or if it's a default sequence pattern (7 digits)
                    if not vals.get('name'):
                        vals['name'] = product.lot_sequence_id._next()
                    elif vals.get('name', '').isdigit() and len(vals.get('name', '')) == 7:
                        # Replace default sequence with product sequence
                        vals['name'] = product.lot_sequence_id._next()

        return super(StockLot, self).create(vals_list)


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.model
    def _get_value_production_lot(self):
        """Override to use product lot sequence in production context"""
        self.ensure_one()

        # Check if product has OCA lot sequence
        if hasattr(self.product_id, 'lot_sequence_id') and self.product_id.lot_sequence_id:
            # Check if we're in a manufacturing context
            if hasattr(self, 'production_id') and self.production_id:
                return self.product_id.lot_sequence_id._next()

        # Fall back to standard behavior
        return super(StockMoveLine, self)._get_value_production_lot()

