# -*- coding: utf-8 -*-
from odoo import models, fields, api
import math


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    fut_size = fields.Selection([
        ('20', '20 Kg'),
        ('25', '25 Kg'),
        ('100', '100 Kg'),
    ], string='Taille du fût', help='Sélectionnez la taille du fût pour ce produit')

    nbr_futs = fields.Float(
        string='Nombre de fûts',
        compute='_compute_nbr_futs',
        digits=(10, 0),
    )

    show_fut_size = fields.Boolean(
        compute='_compute_show_fut_size',
    )

    @api.depends('categ_id')
    def _compute_show_fut_size(self):
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
            rec.show_fut_size = rec.categ_id.id in target_ids

    @api.depends('fut_size', 'qty_available')
    def _compute_nbr_futs(self):
        for rec in self:
            if rec.fut_size and rec.qty_available:
                fut_size = float(rec.fut_size)
                rec.nbr_futs = math.ceil(rec.qty_available / fut_size)
            else:
                rec.nbr_futs = 0