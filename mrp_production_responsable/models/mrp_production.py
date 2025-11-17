from odoo import models, fields, api


class MrpProductionInherit(models.Model):
    _inherit = 'mrp.production'

    responsable_pesee_id = fields.Many2one(
        'res.users',
        string='Responsable pesée',
        tracking=True,
        help='Utilisateur responsable des opérations de pesée'
    )