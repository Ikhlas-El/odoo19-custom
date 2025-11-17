from odoo import models, fields, api


class StockLot(models.Model):
    _inherit = 'stock.lot'

    parent_lot_id = fields.Many2one(
        'stock.lot',
        string='Parent Lot',
        help='The lot from which this lot was produced'
    )

    def _get_first_parent_lot_from_production(self, production_id):
        """Get the first parent lot from a manufacturing order"""
        if not production_id:
            return False

        production = self.env['mrp.production'].browse(production_id)

        cafe_vert = self.env.ref('coffee_maturity.cafe-vert', raise_if_not_found=False)
        cafe_pese = self.env.ref('coffee_maturity.cafe-pese', raise_if_not_found=False)

        # ✅ FIX: Check move_line_ids instead of lot_ids
        for move in production.move_raw_ids:
            for move_line in move.move_line_ids:
                if move_line.lot_id:
                    lot = move_line.lot_id
                    if cafe_vert and lot.product_id.categ_id == cafe_vert:
                        return lot
                    elif cafe_pese and lot.product_id.categ_id == cafe_pese:
                        return lot
        return False

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to inherit lot information from first parent only"""
        lots = super(StockLot, self).create(vals_list)

        for lot in lots:
            if self.env.context.get('default_production_id'):
                parent_lot = self._get_first_parent_lot_from_production(
                    self.env.context.get('default_production_id')
                )

                if parent_lot:
                    lot.write({
                        'parent_lot_id': parent_lot.id,
                        'x_origine_id': parent_lot.x_origine_id.id if parent_lot.x_origine_id else False,
                        'x_espece': parent_lot.x_espece,
                        'x_screen_size': parent_lot.x_screen_size,
                    })

        return lots