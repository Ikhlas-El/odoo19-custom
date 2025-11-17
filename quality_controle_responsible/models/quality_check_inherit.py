from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class QualityCheck(models.Model):
    _inherit = 'quality.check'

    # This field might already exist, but we ensure it's there
    user_id = fields.Many2one('res.users', string='Responsible')

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure user_id is set from quality point if not provided."""
        for vals in vals_list:
            # If user_id not set but point_id is provided
            if 'user_id' not in vals or not vals.get('user_id'):
                point_id = vals.get('point_id')
                if point_id:
                    point = self.env['quality.point'].browse(point_id)
                    if point.user_id:
                        vals['user_id'] = point.user_id.id
                        _logger.info(f"Setting user_id {point.user_id.id} from quality point {point.id}")

        return super().create(vals_list)