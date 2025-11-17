from odoo import models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def write(self, vals):
        """When lot_producing_id is set, copy parent lot data"""
        res = super().write(vals)

        if 'lot_producing_ids' in vals:
            for mo in self:
                if not mo.lot_producing_ids or mo.lot_producing_ids.x_origine_id:
                    continue

                # Find first component lot
                parent_lot = False
                for move in mo.move_raw_ids:
                    for line in move.move_line_ids:
                        if line.lot_id:
                            parent_lot = line.lot_id
                            break
                    if parent_lot:
                        break

                # Copy data
                if parent_lot:
                    mo.lot_producing_ids.parent_lot_id = parent_lot
                    mo.lot_producing_ids.x_origine_id = parent_lot.x_origine_id if parent_lot.x_origine_id else False
                    mo.lot_producing_ids.x_espece = parent_lot.x_espece
                    mo.lot_producing_ids.x_screen_size = parent_lot.x_screen_size

        return res