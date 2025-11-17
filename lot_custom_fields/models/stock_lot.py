from odoo import models, fields, api
import logging
import unicodedata

_logger = logging.getLogger(__name__)

class StockProductionLot(models.Model):
    _inherit = 'stock.lot'

    x_espece = fields.Selection([
        ('arabica', 'Arabica'),
        ('robusta', 'Robusta')
    ], string="Espèce", help="Sélectionnez le type de café")

    # OLD field - keep it to avoid database issues
    x_origine = fields.Selection([
        ('Col', 'Colombie'),
        ('Vit', 'Vietnam'),
        ('ETH', 'Ethiopie'),
        ('Ugh', 'Ouganda'),
        ('Ind', 'Inde')
    ], string="Origine (Old)", help="Deprecated - use x_origine_id instead")

    # NEW Many2one field for origin
    x_origine_id = fields.Many2one(
        'coffee.origin',
        string="Origine",
        help="Sélectionnez le pays d'origine du café",
        ondelete='restrict'
    )

    x_screen_size = fields.Selection([
        ('10', 'Screen 10'),
        ('12', 'Screen 12'),
        ('13', 'Screen 13'),
        ('14', 'Screen 14'),
        ('15', 'Screen 15'),
        ('16', 'Screen 16'),
        ('17', 'Screen 17'),
        ('18', 'Screen 18'),
        ('19', 'Screen 19'),
        ('20', 'Screen 20'),
        ('aa', 'AA'),
        ('ab', 'AB'),
        ('pb', 'Peaberry'),
        ('excelso', 'Excelso'),
        ('supremo', 'Supremo'),
        ('g1', 'Grade 1 (G1)'),
    ], string="Screen Size", help="Sélectionnez screen size des grains de café")

    show_cafe_vert_fields = fields.Boolean(
        string="Afficher les champs de cafe vert",
        compute="_compute_show_cafe_vert_fields",
        store=True
    )

    clean_product_name = fields.Char(
        string='Clean Product Name',
        compute='_compute_clean_product_name',
        store=False,
        help='Product name with proper encoding'
    )

    qr_data = fields.Text(
        string='QR Data',
        compute='_compute_qr_data',
        store=False,
        help='Combined data for QR code generation'
    )

    @api.depends('product_id', 'product_id.categ_id')
    def _compute_show_cafe_vert_fields(self):
        category_cafe_vert = self.env.ref('coffee_maturity.cafe-vert', raise_if_not_found=False)
        category_cafe_pese = self.env.ref('coffee_maturity.cafe-pese', raise_if_not_found=False)
        category_cafe_tor = self.env.ref('coffee_maturity.cafe-tor', raise_if_not_found=False)

        for lot in self:
            lot.show_cafe_vert_fields = False

            if (lot.product_id and
                    lot.product_id.categ_id and
                    lot.product_id.categ_id in (category_cafe_vert, category_cafe_pese, category_cafe_tor)):
                lot.show_cafe_vert_fields = True

    def _remove_accents(self, text):
        if not text:
            return ""
        try:
            text = unicodedata.normalize('NFKD', text)
            text = ''.join([c for c in text if not unicodedata.combining(c)])
            return text
        except:
            return text

    def _fix_encoding(self, text):
        if not text:
            return ""
        try:
            if 'Ã©' in text:
                text = text.encode('latin-1').decode('utf-8')
            return text
        except:
            return text

    @api.depends('product_id')
    def _compute_clean_product_name(self):
        for lot in self:
            if lot.product_id:
                clean_name = lot.product_id.name or lot.product_id.display_name or ""
                clean_name = self._fix_encoding(clean_name)
                lot.clean_product_name = clean_name
            else:
                lot.clean_product_name = ""

    @api.depends('name', 'product_id', 'x_espece', 'x_origine_id', 'x_screen_size')
    def _compute_qr_data(self):
        for lot in self:
            try:
                qr_parts = []

                if lot.name:
                    qr_parts.append(f"LOT: {lot.name}")

                if lot.product_id and lot.product_id.display_name:
                    product_name = self._remove_accents(lot.product_id.display_name)
                    qr_parts.append(f"PRODUIT: {product_name}")

                if lot.x_espece:
                    espece_label = dict(self._fields['x_espece'].selection).get(lot.x_espece, lot.x_espece)
                    qr_parts.append(f"ESPECE: {espece_label}")

                # Use the new Many2one field for origin
                if lot.x_origine_id:
                    qr_parts.append(f"ORIGINE: {lot.x_origine_id.name}")

                if lot.x_screen_size:
                    size_label = dict(self._fields['x_screen_size'].selection).get(
                        lot.x_screen_size, lot.x_screen_size
                    )
                    qr_parts.append(f"SCREEN SIZE: {size_label}")

                qr_text = "\n".join(qr_parts)
                _logger.info(f"QR generated for lot {lot.name}: {repr(qr_text)}")
                lot.qr_data = qr_text

            except Exception as e:
                _logger.error(f"QR generation error for lot {lot.id if lot else 'None'}: {str(e)}")
                lot.qr_data = f"LOT: {lot.name}" if lot and lot.name else "LOT: ERROR"


