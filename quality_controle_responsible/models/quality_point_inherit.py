from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class QualityPoint(models.Model):
    _inherit = 'quality.point'

    def _get_check_values(self, record, **kwargs):
        """Override to add user_id to check values from quality point."""
        values = super()._get_check_values(record, **kwargs)

        # Add user_id from quality point to the check
        if self.user_id:
            values['user_id'] = self.user_id.id
            _logger.info(f"Setting user_id {self.user_id.id} for quality check from point {self.id}")

        return values