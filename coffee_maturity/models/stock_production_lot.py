# models/stock_production_lot.py
from odoo import models, fields, api


class StockProductionLot(models.Model):
    _inherit = 'stock.lot'

    production_date = fields.Datetime(
        string="Date de production",
        readonly=True,
        help="La date réelle à laquelle ce lot a été produit (depuis l'OF)."
    )

    niveau_torrefaction = fields.Selection(
        [
            ('espresso', 'Espresso'),
            ('light', 'Light'),
            ('medium', 'Medium'),
            ('dark', 'Dark'),
        ],
        string="Niveau de Torréfaction",
        help = "Sélectionnez le niveau de torréfaction du café."
    )

    maturity_time = fields.Char(
        string="Durée de maturité",
        compute="_compute_maturity_time",
        help="Temps écoulé depuis la date de production (en jours et heures)."
    )

    show_maturity_fields = fields.Boolean(
        string="Afficher les champs de maturité",
        compute="_compute_show_maturity_fields",
        store=True
    )

    @api.depends('production_date')
    def _compute_maturity_time(self):
        now = fields.Datetime.now()
        for lot in self:
            if lot.production_date:
                delta = now - lot.production_date
                days = delta.days
                hours = delta.seconds // 3600

                day_label = "jour" if days == 1 else "jours"
                hour_label = "heure" if hours == 1 else "heures"

                lot.maturity_time = f"{days} {day_label} {hours} {hour_label}"
            else:
                lot.maturity_time = "0 jour 0 heure"


    @api.depends('product_id', 'product_id.categ_id')
    def _compute_show_maturity_fields(self):
        # get the category record
        category_cafe = self.env.ref('coffee_maturity.cafe-tor', raise_if_not_found=False)

        for lot in self:
            # print(
            #     f"Lot {lot.name}: Product={lot.product_id.name if lot.product_id else 'None'}, Category={lot.product_id.categ_id.name if lot.product_id and lot.product_id.categ_id else 'None'}")

            lot.show_maturity_fields = False

            if (lot.product_id and
                    lot.product_id.categ_id and
                    category_cafe and
                    lot.product_id.categ_id == category_cafe):
                lot.show_maturity_fields = True
                # print(f"  -> Showing maturity fields for {lot.name}")


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def button_mark_done(self):
        res = super().button_mark_done()
        for mo in self:
            if mo.date_finished:
                for move in mo.move_finished_ids:
                    for ml in move.move_line_ids:
                        if ml.lot_id:
                            ml.lot_id.production_date = mo.date_finished
        return res

