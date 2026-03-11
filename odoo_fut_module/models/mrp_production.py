# -*- coding: utf-8 -*-
from odoo import models, fields, api
import math


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    fut_line_ids = fields.One2many(
        'mrp.fut.line',
        'production_id',
        string='Lignes Fût'
    )

    show_fut_tab = fields.Boolean(
        string='Afficher onglet Fût',
        compute='_compute_show_fut_tab',
    )

    @api.depends('product_id', 'product_id.categ_id')
    def _compute_show_fut_tab(self):
        target_ids = []
        for xml_id in [
            'coffee_maturity.cafe-pese',
            'coffee_maturity.cafe-tor',
            'coffee_maturity.cafe-mel',
        ]:
            cat = self.env.ref(xml_id, raise_if_not_found=False)
            if cat:
                target_ids.append(cat.id)
        for rec in self:
            rec.show_fut_tab = bool(
                rec.product_id and rec.product_id.categ_id.id in target_ids
            )

    def _get_responsable_id(self):
        try:
            val = self.responsable_pesee_id
            return val.id if val and val.id else False
        except AttributeError:
            return False

    def _get_conducteur_id(self):
        for wo in self.workorder_ids.sorted('sequence'):
            if wo.employee_assigned_ids:
                return wo.employee_assigned_ids[0].id
        return False

    def _generate_fut_lines_vals(self):
        if not (self.product_id and self.product_qty and self.product_id.fut_size):
            return []
        fut_size = float(self.product_id.fut_size)
        total_qty = self.product_qty
        num_futs = math.ceil(total_qty / fut_size)
        responsable_id = self._get_responsable_id()
        conducteur_id = self._get_conducteur_id()
        lines = []
        for i in range(num_futs):
            qty = min(fut_size, total_qty - i * fut_size)
            lines.append((0, 0, {
                'fut_number': i + 1,
                'quantite': qty,
                'responsable_pesee_id': responsable_id,
                'conducteur_machine_id': conducteur_id,
            }))
        return lines

    @api.onchange('product_id', 'product_qty')
    def _onchange_product_generate_fut_lines(self):
        self.fut_line_ids = [(5, 0, 0)]
        self.fut_line_ids = self._generate_fut_lines_vals()

    @api.onchange('responsable_pesee_id')
    def _onchange_responsable_update_fut_lines(self):
        if not self.fut_line_ids:
            return
        responsable_id = self._get_responsable_id()
        for line in self.fut_line_ids:
            line.responsable_pesee_id = responsable_id

    def write(self, vals):
        res = super().write(vals)
        if 'responsable_pesee_id' in vals:
            for production in self:
                responsable_id = production._get_responsable_id()
                empty_lines = production.fut_line_ids.filtered(
                    lambda l: not l.responsable_pesee_id
                )
                if empty_lines and responsable_id:
                    empty_lines.write({'responsable_pesee_id': responsable_id})
        return res

    def action_regenerate_fut_lines(self):
        self.ensure_one()
        self.fut_line_ids.unlink()
        fut_size = float(self.product_id.fut_size)
        total_qty = self.product_qty
        num_futs = math.ceil(total_qty / fut_size)
        responsable_id = self._get_responsable_id()
        conducteur_id = self._get_conducteur_id()
        for i in range(num_futs):
            qty = min(fut_size, total_qty - i * fut_size)
            self.env['mrp.fut.line'].create({
                'production_id': self.id,
                'fut_number': i + 1,
                'quantite': qty,
                'responsable_pesee_id': responsable_id,
                'conducteur_machine_id': conducteur_id,
            })
        return True